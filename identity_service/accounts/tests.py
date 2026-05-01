from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from accounts.models import Profile, User, UserDevice
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import RequestFactory, TestCase
from common.middleware import DistributedTracingMiddleware, get_current_trace_id
import uuid
from django.http import HttpResponse
from accounts.services import AuthService
from user_sessions.models import ActiveSession
from unittest.mock import patch
from django.urls import reverse

User = get_user_model()

class ParentTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.registrar = cls.create_test_user(email = 'registrar@gmail.com', username = 'registrar_user', 
      control = 'registrar', cnic = '65111-9797111-1')
    cls.citizen = cls.create_test_user(email = 'citizen@gmail.com', username = 'citizen_user', 
      control = 'citizen', cnic = '65222-87982222-2')
    cls.tehsildar = cls.create_test_user(email = 'teh@gmail.com', username = 'teh_user', control = 'tehsildar', cnic = '65233-97973333-3')

  @staticmethod
  def create_test_user(email, username, control, cnic):
    user = User.objects.create_user(email=email, username=username, password = 'root12312', control=control, cnic=cnic)
    Profile.objects.get_or_create(user=user, full_name=f'{username} Full Name')
    return user

  def get_token(self, user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

  def auth_headers(self, user):
    return {'HTTP_AUTHORIZATION': f'Bearer {self.get_token(user)}'}

  def test_check(self):
    self.assertEqual(self.registrar.username, 'registrar_user')
    self.assertEqual(self.citizen.username, 'citizen_user')
    self.assertEqual(self.tehsildar.username, 'teh_user')
    
# class TestTracingMiddleware(TestCase):
#   def setUp(self):
#     self.factory = RequestFactory()
#     self.get_response = lambda req: req.response if hasattr(req, 'response') else type('Response', (), {})()
#     self.middleware = DistributedTracingMiddleware(self.get_response)

#   def test_trace_id_generation(self):
#     request = self.factory.get('/')
        
#     def get_response(req):
#       self.assertIsNotNone(get_current_trace_id())
#       return HttpResponse()
#     middleware = DistributedTracingMiddleware(get_response)
#     response = middleware(request)
#     self.assertIn('X-Trace-ID', response)
#     self.assertIsNone(get_current_trace_id())
#     print('the new trace id is generated')

#   def test_trace_id_propagation(self):
#     incoming_trace_id = str(uuid.uuid4())
#     request = self.factory.get('/', HTTP_X_TRACE_ID=incoming_trace_id)

#     def get_response(req):
#       self.assertEqual(get_current_trace_id(), incoming_trace_id)
#       return HttpResponse()
#     middleware = DistributedTracingMiddleware(get_response)
#     response = middleware(request)
#     self.assertEqual(response['X-Trace-ID'], incoming_trace_id)
#     print(f'trace id {incoming_trace_id}')

#   def test_thread_local_cleanup(self):
#     request = self.factory.get('/')

#     def get_response_fail(req):
#       raise Exception('view is stopped')
#     middleware = DistributedTracingMiddleware(get_response_fail)
#     with self.assertRaises(Exception):
#       middleware(request)
#     self.assertIsNone(get_current_trace_id())
#     print('the thread local is cleaned')
    
# class TestAuthService(TestCase):
#   def test_hash_cnic_consistency(self):
#     raw_cnic = '42101-1234567-1'
#     hash1 = AuthService.hash_cnic(raw_cnic)
#     hash2 = AuthService.hash_cnic(raw_cnic)
#     self.assertEqual(hash1, hash2)
#     self.assertNotEqual(hash1, raw_cnic)

#   def test_register_user_creates_profile(self):
#     data = {'username': 'tehsildar_punjab', 'email': 'tehsildar@punjab.gov.pk', 'password': 'teh12312'}
#     raw_cnic = '42101-1234567-1'
#     user = AuthService.register_user(data, raw_cnic)
#     self.assertTrue(User.objects.filter(email=data['email']).exists())
#     self.assertTrue(Profile.objects.filter(user=user).exists())
#     profile = Profile.objects.get(user=user)
#     self.assertEqual(profile.cnic_hash, AuthService.hash_cnic(raw_cnic))

#   def test_register_device_by_email(self):
#     user = User.objects.create_user(username = 'citizen1', email = 'citizen@gmail.com', password = 'cit12312')
#     fingerprint = 'browser-fingerprint-xyz-123' 
#     device = AuthService.register_device_by_email(user.email, fingerprint)
#     self.assertIsNotNone(device)
#     self.assertEqual(device.device_fingerprint, fingerprint)
    
class TestAccountLock(TestCase):
  def test_on_account_lock_clears_sessions(self):
    user = User.objects.create_user(username = 'user1', email = 'user1@gmail.com', password = 'user112312')
    ActiveSession.objects.create(user=user, session_key="dummy-key", ip_address = '127.0.0.1')
    self.assertEqual(ActiveSession.objects.filter(user=user).count(), 1)
    user.is_active = False
    user.save()
    self.assertEqual(ActiveSession.objects.filter(user=user).count(), 0)
    
class TestAuthenticationViewsrt(APITestCase):
  def setUp(self):
    self.client = APIClient()
    self.register_url = reverse('identity-register')
    self.me_url = reverse('identity-me')
    self.login_url = reverse('token_obtain_pair')

  def test_register_flow(self):
    data = {'username': 'citizen_root', 'email': 'root@gmail.com', 'password': 'root12312', 'cnic': '42101-1234567-1'}
    response = self.client.post(self.register_url, data, format = 'json')
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.data['email'], 'root@gmail.com')
    self.assertTrue(User.objects.filter(username = 'citizen_root').exists())

  def test_token_obtain_pair(self):
    user = User.objects.create_user(username = 'device_user', email = 'device@gmail.com', password = 'dev12312')
    login_data = {'email': 'device@gmail.com', 'password': 'dev12312'}
    fingerprint_id = 'unique-hardware-id-23'
    headers = {'HTTP_X_DEVICE_FINGERPRINT': fingerprint_id}
    response = self.client.post(self.login_url, login_data, **headers)
    self.assertEqual(response.status_code, 200)
    self.assertIn('access', response.data)
    self.assertTrue(UserDevice.objects.filter(user=user, device_fingerprint=fingerprint_id).exists())

  def test_me_endpoint_permission_denied(self):
    response = self.client.get(self.me_url)
    self.assertEqual(response.status_code, 401)

  @patch('common.permissions.LandPermission.has_permission')
  @patch('accounts.views.AuthenticationViewSet.get_queryset')
  def test_me_endpoint_done(self, mock_get_queryset, mock_land_perm):
    mock_land_perm.return_value = True
    user = User.objects.create_user(username='user2', email = 'user2@gmail.com', password = 'user212312')
    self.client.force_authenticate(user=user)
    response = self.client.get(self.me_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['username'], 'user2')