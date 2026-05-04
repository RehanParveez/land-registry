from django.test import TransactionTestCase, RequestFactory
from contracts.models import Agreement
import uuid
from contracts.services import ContractStateMachine
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, patch
from django.http import JsonResponse
from escrow_center.middleware import UnchangedMiddleware
import json

class TestContractStateMachine(TransactionTestCase):
  def setUp(self):
    self.agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=uuid.uuid4(), seller_uuid=uuid.uuid4(),
      agreed_price=100000.00, status = 'draft')

  def test_transition_valid_flow(self):
    ContractStateMachine.transition(self.agreement, 'funded')
    self.agreement.refresh_from_db()
    self.assertEqual(self.agreement.status, 'funded')

  def test_transition_invalid_jump(self):
    with self.assertRaises(ValidationError) as cm:
      ContractStateMachine.transition(self.agreement, 'completed')
    self.assertIn('draft to completed', str(cm.exception))
    self.agreement.refresh_from_db()
    self.assertEqual(self.agreement.status, 'draft')

  def test_transition_to_same_status(self):
    updated = ContractStateMachine.transition(self.agreement, 'draft')
    self.assertEqual(updated.status, 'draft')

  def test_cancelled_is_terminal(self):
    self.agreement.status = 'cancelled'
    self.agreement.save()
    with self.assertRaises(ValidationError):
      ContractStateMachine.transition(self.agreement, 'funded')
      
class TestAgreementViewSet(APITestCase):
  def setUp(self):
    self.base_url = '/contracts/agreement/'
    self.buyer_id = str(uuid.uuid4())
    self.seller_id = str(uuid.uuid4())
    self.other_id = str(uuid.uuid4())
    self.my_agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=self.buyer_id,
      seller_uuid=self.seller_id, agreed_price=100000.00, status = 'draft')
    self.other_agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=self.other_id,
      seller_uuid=str(uuid.uuid4()), agreed_price=200000.00, status = 'draft')

  def test_get_queryset_filtering_for_citizen(self):
    token_payload = {'user_id': self.buyer_id, 'control': 'citizen'}
    self.client.force_authenticate(user=None, token=token_payload)
    response = self.client.get(self.base_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(str(response.data[0]['id']), str(self.my_agreement.id))

  def test_perform_create_assigns_buyer(self):
    token_payload = {'user_id': self.buyer_id, 'control': 'citizen'}
    self.client.force_authenticate(user=None, token=token_payload)
    data = {'parcel_id': str(uuid.uuid4()), 'seller_uuid': self.seller_id, 'agreed_price': '50000.00'}
    response = self.client.post(self.base_url, data)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.data['buyer_uuid'], self.buyer_id)
    self.assertEqual(response.data['status'], 'draft')

  def test_registrar_sees_all(self):
    token_payload = {'user_id': str(uuid.uuid4()), 'control': 'registrar'}
    self.client.force_authenticate(user=None, token=token_payload)
    response = self.client.get(self.base_url)
    self.assertEqual(len(response.data), 2)
    
class TestUnchangedMiddleware(TransactionTestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.get_response = MagicMock(return_value=JsonResponse({'id': 1}, status=201))
    self.redis_patcher = patch('redis.Redis')
    self.mock_redis_class = self.redis_patcher.start()
    self.mock_redis = self.mock_redis_class.return_value
    self.middleware = UnchangedMiddleware(self.get_response)

  def tearDown(self):
    self.redis_patcher.stop()

  def test_middleware_ignores_get_requests(self):
    request = self.factory.get('/contracts/agreement/')
    self.middleware(request)  
    self.mock_redis.get.assert_not_called()
    self.get_response.assert_called_once()

  def test_middleware_caches_new_post_request(self):
    self.mock_redis.get.return_value = None  
    request = self.factory.post('/contracts/agreement/', data=json.dumps({'parcel_id': 'abc'}), 
      content_type = 'application/json', HTTP_UNCHANGED_KEY = 'unique-req-123')
    response = self.middleware(request)
    self.assertEqual(response.status_code, 201)
    self.assertTrue(self.mock_redis.setex.called)
    cache_key = 'unchanged:unique-req-123'
    self.assertEqual(self.mock_redis.setex.call_args[0][0], cache_key)

  def test_middleware_blocks_duplicate_post_request(self):
    cached_payload = json.dumps({'body': {'id': 99, 'status': 'cached'}, 'status': 201})
    self.mock_redis.get.return_value = cached_payload
    request = self.factory.post('/contracts/agreement/', HTTP_UNCHANGED_KEY = 'duplicate-key')
    response = self.middleware(request)
    self.get_response.assert_not_called()
    self.assertEqual(response.status_code, 201)
    self.assertEqual(json.loads(response.content)['id'], 99)