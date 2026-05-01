from accounts.tests import ParentTestCase
from rest_framework.test import APIRequestFactory
from user_sessions.middleware import SessionHardeningMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from user_sessions.models import ActiveSession
from unittest.mock import patch

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