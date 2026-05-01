from accounts.tests import ParentTestCase
from rest_framework.test import APIRequestFactory
from user_sessions.middleware import SessionHardeningMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from user_sessions.models import ActiveSession
from unittest.mock import patch
from django.urls import reverse
from unittest.mock import patch, PropertyMock

class TestSessionHardening(ParentTestCase):
  def setUp(self):
    self.factory = APIRequestFactory()
    self.middleware = SessionHardeningMiddleware(lambda req: None)

  def _add_session_to_request(self, request):
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

  def test_create_active_session_record(self):
    request = self.factory.get('/', REMOTE_ADDR = '192.168.1.1')
    request.user = self.citizen 
    self._add_session_to_request(request)
    self.middleware.process_request(request)
    self.assertTrue(ActiveSession.objects.filter(user=self.citizen, ip_address = '192.168.1.1').exists())
    print(f'the record created {self.citizen.email}')

  def test_ip_mismatch_causing_logout(self):
    raw_token = 'check-token-23'
    session_key = f'Bearer {raw_token}'
    ActiveSession.objects.create(user=self.tehsildar, session_key=session_key, ip_address = '10.0.0.1')

    request = self.factory.get('/', HTTP_AUTHORIZATION = session_key, REMOTE_ADDR = '10.0.0.2')
    request.user = self.tehsildar
    self._add_session_to_request(request)
    print(f'db contains: {ActiveSession.objects.filter(session_key=session_key).exists()}')
    print(f'header sent: {session_key}')
    with patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate') as mock_auth:
      mock_auth.return_value = (self.tehsildar, 'token_obj')
      self.middleware.process_request(request)
    act_session = ActiveSession.objects.get(session_key=session_key)
    self.assertTrue(act_session.is_flagged)
    print(f'the ip mismatch {self.tehsildar.email}')
    
class TestSessionViewSet(ParentTestCase):
  def setUp(self):
    self.list_url = reverse('session-list')
    self.citizen_session = ActiveSession.objects.create(user=self.citizen, ip_address = '127.0.0.1', device_type = 'Mobile')
    self.teh_session = ActiveSession.objects.create(user=self.tehsildar, ip_address = '192.168.1.1', device_type = 'Desktop')

  @patch('common.permissions.LandPermission.has_permission')
  def test_get_queryset_citizen_only(self, mock_perm):
    mock_perm.return_value = True
    self.client.force_authenticate(user=self.citizen)

    with patch('rest_framework.request.Request.auth', new_callable=PropertyMock) as mock_auth:
      mock_auth.return_value = {'control': 'citizen'}
      with patch('rest_framework.request.Request.user_id', self.citizen.id, create=True):
        response = self.client.get(self.list_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['ip_address'], '127.0.0.1')

  @patch('common.permissions.LandPermission.has_permission')
  def test_get_queryset_registrar_sees_all(self, mock_perm):
    mock_perm.return_value = True
    self.client.force_authenticate(user=self.registrar)
    with patch('rest_framework.request.Request.auth', new_callable=PropertyMock) as mock_auth:
      mock_auth.return_value = {'control': 'registrar'}
      with patch('rest_framework.request.Request.user_id', self.registrar.id, create=True):
        response = self.client.get(self.list_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 2)

  @patch('common.permissions.LandPermission.has_permission')
  def test_terminate_session_destroy(self, mock_perm):
    mock_perm.return_value = True
    self.client.force_authenticate(user=self.citizen)
    url = reverse('session-detail', kwargs={'pk': self.citizen_session.pk})
    with patch('rest_framework.request.Request.user_id', self.citizen.id, create=True):
      response = self.client.delete(url)
    self.assertEqual(response.status_code, 204)
    self.assertFalse(ActiveSession.objects.filter(pk=self.citizen_session.pk).exists())