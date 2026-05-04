import pytest
from contracts.models import Agreement
import uuid
from decimal import Decimal
from payments.models import Wallet
from unittest.mock import patch, MagicMock, PropertyMock
from process.services import TransferProcessOperator
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestTransferProcess:
  @pytest.fixture
  def setup_data(self):
    agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=uuid.uuid4(), seller_uuid=uuid.uuid4(),
      agreed_price=Decimal('5000.00'), status = 'funded')
    wallet, created = Wallet.objects.get_or_create(agreement=agreement)
    wallet.balance=Decimal('5000.00')
    wallet.save()
    return agreement, wallet

  @patch('process.services.breaker_call')
  def test_execute_full_success(self, mock_breaker, setup_data):
    agreement, wallet = setup_data
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_breaker.return_value = (mock_res, None)
    result = TransferProcessOperator.execute(agreement_id=agreement.id, auth_token = 'Bearer test-token')
    
    assert result['success'] is True
    agreement.refresh_from_db()
    assert agreement.status == 'completed'
    assert mock_breaker.call_count == 3

  @patch('process.services.breaker_call')
  @patch('requests.patch')
  def test_execute_biometric_failure_triggers_abort(self, mock_unlock, mock_breaker, setup_data):
    agreement, wallet = setup_data
    lock_res = MagicMock()
    lock_res.status_code = 200
    bio_res = MagicMock()
    bio_res.status_code = 400
    mock_breaker.side_effects = [(lock_res, None), (bio_res, None)]
    mock_breaker.side_effect = [(lock_res, None), (bio_res, None)]
    result = TransferProcessOperator.execute(agreement.id)
    
    assert result['success'] is False
    assert 'biometric match failed' in result['err']
    agreement.refresh_from_db()
    assert agreement.status == 'cancelled'
    assert mock_unlock.called 

  @patch('process.services.breaker_call')
  def test_execute_insufficient_funds(self, mock_breaker, setup_data):
    agreement, wallet = setup_data
    wallet.balance = Decimal('100.00')
    wallet.save()
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_breaker.side_effect = [(mock_res, None), (mock_res, None)]
    result = TransferProcessOperator.execute(agreement.id)
    
    assert result['success'] is False
    assert 'funds are less' in result['err']
    agreement.refresh_from_db()
    assert agreement.status == 'cancelled'

  @patch('process.services.breaker_call')
  def test_circuit_breaker_open_error(self, mock_breaker, setup_data):
    agreement, wallet = setup_data
    mock_breaker.return_value = (None, 'the circuit is open. and depend serv is down.')
    result = TransferProcessOperator.execute(agreement.id)
    
    assert result['success'] is False
    assert 'circuit is open' in result['err']
    agreement.refresh_from_db()
    assert agreement.status == 'cancelled'
    
@pytest.mark.django_db
class TestProcessViewSet:
  @pytest.fixture
  def api_client(self):
    return APIClient()

  @pytest.fixture
  def setup_transfer_data(self):
    agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=uuid.uuid4(), seller_uuid=uuid.uuid4(),
      agreed_price=Decimal('1000.00'), status = 'funded')
    wallet, created = Wallet.objects.get_or_create(agreement=agreement)
    wallet.balance = Decimal('1000.00')
    wallet.save()
    return agreement

  @patch('process.views.TransferProcessOperator.execute')
  def test_start_transfer_success(self, mock_execute, api_client, setup_transfer_data):
    agreement = setup_transfer_data
    url = '/process/transfer/start_transfer/'
    mock_execute.return_value = {'success': True, 'message': 'Done'}
    token_payload = {'control': 'registrar', 'user_id': str(uuid.uuid4())}
    api_client.credentials(HTTP_AUTHORIZATION='Bearer valid-token')
    with patch('process.views.ProcessViewSet.authentication_classes', []), \
      patch('common.permissions.LandPermission.has_permission', return_value=True), \
      patch('common.permissions.EnoughEscrowPermission.has_permission', return_value=True):
        
      with patch('rest_framework.request.Request.auth', PropertyMock(return_value=token_payload)):
        response = api_client.post(url, {'agreement_id': str(agreement.id), 'shard': 'punjab'}, format = 'json')
    assert response.status_code == 200
    assert response.data['success'] is True
    mock_execute.assert_called_once()

  def test_start_transfer_missing_agreement_id(self, api_client):
    url = '/process/transfer/start_transfer/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer valid-token')
    with patch('process.views.ProcessViewSet.authentication_classes', []), \
      patch('common.permissions.LandPermission.has_permission', return_value=True), \
      patch('common.permissions.EnoughEscrowPermission.has_permission', return_value=True):
      response = api_client.post(url, {'shard': 'punjab'}, format = 'json')
    assert response.status_code == 400
    assert 'agreement_id is needed' in response.data['err']

  def test_enough_escrow_permission_denied(self, api_client, setup_transfer_data):
    agreement = setup_transfer_data
    wallet = Wallet.objects.get(agreement=agreement)
    wallet.balance = Decimal('50.00')
    wallet.save()
    url = '/process/transfer/start_transfer/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer valid-token')
    with patch('process.views.ProcessViewSet.authentication_classes', []), \
      patch('common.permissions.LandPermission.has_permission', return_value=True):
      response = api_client.post(url, {'agreement_id': str(agreement.id)}, format = 'json')
    assert response.status_code == 403