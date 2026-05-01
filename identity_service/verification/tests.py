from django.test import TestCase
from accounts.models import User, Profile
from verification.models import VerificationRec
from unittest.mock import patch
from verification.services import BiometricService
from unittest.mock import patch
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch, PropertyMock

# class TestUpdateProfile(TestCase):
#   def setUp(self):
#     self.user = User.objects.create_user(username = 'user3', email = 'user3@gmail.com', password = 'user312312')
#     self.profile, created = Profile.objects.get_or_create(user=self.user)
#     self.profile.is_verified = False
#     self.profile.save()

#   def test_profile_verified_on_success(self):
#     VerificationRec.objects.create(user=self.user, method = 'cnic', status = 'success')
#     self.profile.refresh_from_db()
#     self.assertTrue(self.profile.is_verified)

#   def test_profile_not_verified(self):
#     VerificationRec.objects.create(user=self.user, method = 'biometric', status = 'failed')
#     self.profile.refresh_from_db()
#     self.assertFalse(self.profile.is_verified)

#   def test_dont_re_save_if_already_verified(self):
#     self.profile.is_verified = True
#     self.profile.save()
#     VerificationRec.objects.create(user=self.user, method = 'manual', status = 'success')
#     self.profile.refresh_from_db()
#     self.assertTrue(self.profile.is_verified)
    
# class TestBiometricService(TestCase):
#   def test_wrong_scan_returns_false(self):
#     result = BiometricService.verify_hash('INVALID_SCAN')
#     self.assertFalse(result)

#   @patch('random.random')
#   def test_verify_hash_success(self, mock_random):
#     mock_random.return_value = 0.5
#     result = BiometricService.verify_hash('check_hash')
#     self.assertTrue(result)

#   @patch('random.random')
#   def test_verify_hash_failure(self, mock_random):
#     mock_random.return_value = 0.05
#     result = BiometricService.verify_hash('user_auth_hash')
#     self.assertFalse(result)

#   @patch('time.sleep', return_value=None)
#   def test_performance(self, mock_sleep):
#     BiometricService.verify_hash('value_hash')
#     self.assertTrue(mock_sleep.called)
    
class TestVerificationViewSet(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(username = 'user4', email = 'user4@gmail.com', password = 'user412312', control = 'citizen')
    self.profile = Profile.objects.create(user=self.user)
    self.url = reverse('verify-verify-biometric')

  @patch('common.permissions.LandPermission.has_permission')
  @patch('verification.services.BiometricService.verify_hash')
  def test_verify_biometric_success(self, mock_verify, mock_perm):
    mock_verify.return_value = True
    mock_perm.return_value = True
    self.client.force_authenticate(user=self.user)
    with patch('rest_framework.request.Request.user_id', self.user.id, create=True):
      response = self.client.post(self.url, {'hash': 'valid_hash'}, format = 'json')
    self.assertEqual(response.status_code, 200)
    self.assertTrue(VerificationRec.objects.filter(user=self.user, status = 'success').exists())
  
  @patch('common.permissions.LandPermission.has_permission')
  @patch('verification.services.BiometricService.verify_hash')
  def test_verify_biometric_failure(self, mock_verify, mock_perm):
    mock_verify.return_value = False
    mock_perm.return_value = True
    self.client.force_authenticate(user=self.user)
    with patch('rest_framework.request.Request.user_id', self.user.id, create=True):
      response = self.client.post(self.url, {'hash': 'invalid_hash'}, format = 'json')
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response.data['message'], 'the biometric match has failed')
    self.assertTrue(VerificationRec.objects.filter(user=self.user, status = 'failed').exists())

  @patch('common.permissions.LandPermission.has_permission')
  def test_verify_biometric_no_hash(self, mock_perm):
    mock_perm.return_value = True
    self.client.force_authenticate(user=self.user)
    with patch('rest_framework.request.Request.user_id', self.user.id, create=True):
      response = self.client.post(self.url, {}, format = 'json')
    self.assertEqual(response.status_code, 400)
    self.assertIn('err', response.data)
    self.assertEqual(response.data['err'], 'no biomet hash was provided')

  @patch('common.permissions.LandPermission.has_permission')
  def test_get_queryset_registrar_sees_all(self, mock_perm):
    mock_perm.return_value = True
    VerificationRec.objects.create(user=self.user, method = 'biometric', status = 'success')
    new_user = User.objects.create_user(username = 'user5', email = 'user5@gmail.com')
    VerificationRec.objects.create(user=new_user, method = 'manual', status = 'pending')
    self.client.force_authenticate(user=self.user)
    with patch('rest_framework.request.Request.auth', new_callable=PropertyMock) as mock_auth:
      mock_auth.return_value = {'control': 'registrar'}
      with patch('rest_framework.request.Request.user_id', self.user.id, create=True):
       url = reverse('verify-list') 
       response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 2)