from django.test import TransactionTestCase
from django.core.cache import cache
from parcels.test_utils import create_land_hierarchy
from parcels.services import ParcelLockService
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from unittest.mock import patch

class TestParcelLockService(TransactionTestCase):
  databases = {'default', 'punjab', 'sindh'}

  def setUp(self):
    cache.clear()
    self.shard = 'punjab'
    self.parcel, self.mauza = create_land_hierarchy(self.shard)

  def test_acquire_lock_success(self):
    success, message = ParcelLockService.acquire_lock(self.parcel.id, self.shard)
    self.parcel.refresh_from_db(using=self.shard)
    self.assertTrue(success)
    self.assertEqual(self.parcel.status, 'locked')
    self.assertEqual(cache.get(f'lock:parcel:{self.shard}:{self.parcel.id}'), 'locked')

  def test_acquire_lock_already_cached(self):
    lock_key = f'lock:parcel:{self.shard}:{self.parcel.id}'
    cache.set(lock_key, 'locked')  
    success, message = ParcelLockService.acquire_lock(self.parcel.id, self.shard)
    self.assertFalse(success)
    self.assertEqual(message, 'the parcel is curr locked')

  def test_acquire_lock_not_available_in_db(self):
    self.parcel.status = 'pending'
    self.parcel.save(using=self.shard) 
    success, message = ParcelLockService.acquire_lock(self.parcel.id, self.shard)   
    self.assertFalse(success)
    self.assertEqual(message, 'the parcel is not avail')

  def test_release_lock_success(self):
    self.parcel.status = 'locked'
    self.parcel.save(using=self.shard)
    cache.set(f'lock:parcel:{self.shard}:{self.parcel.id}', 'locked') 
    success, message = ParcelLockService.release_lock(self.parcel.id, self.shard) 
    self.parcel.refresh_from_db(using=self.shard)
    self.assertTrue(success)
    self.assertEqual(self.parcel.status, 'available')
    self.assertIsNone(cache.get(f'lock:parcel:{self.shard}:{self.parcel.id}'))
    
class TestParcelViewSet(APITestCase):
  databases = {'default', 'punjab', 'sindh'}

  def setUp(self):
    cache.clear()
    self.shard = 'sindh'
    self.parcel, self.mauza = create_land_hierarchy(self.shard)
    self.user = User.objects.create_superuser(username = 'regisuser', password = 'reg12312', email = 'reg@gmail.com')
    self.base_url = f'/{self.shard}/parcels/parcel/'
    self.lock_url = f'{self.base_url}{self.parcel.id}/lock/'
    self.unlock_url = f'{self.base_url}{self.parcel.id}/unlock/'

  def test_list_parcels_from_correct_shard(self):
    self.client.force_authenticate(user=self.user)
    with patch('common.permissions.LandPermission.has_permission', return_value=True), \
      patch('common.permissions.RegistrarPermission.has_permission', return_value=True):
      response = self.client.get(self.base_url)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.data), 1)
      self.assertEqual(response.data[0]['khasra_number'], 'KH-23')

  def test_lock_parcel_action(self):
    headers = {'HTTP_INTERNAL_SERVICE_TOKEN': 'land-registry-internal-secret-2026',
      'HTTP_X_INTERNAL_SERVICE': 'true'}
    response = self.client.patch(self.lock_url, **headers)
    if response.status_code != 200:
      print(f'error detail: {response.data}')
    self.assertEqual(response.status_code, 200)
    self.parcel.refresh_from_db(using=self.shard)
    self.assertEqual(self.parcel.status, 'locked')
    self.assertEqual(response.data['detail'], 'the parcel is locked for 30 mins')

  def test_unlock_parcel(self):
    self.parcel.status = 'locked'
    self.parcel.save(using=self.shard)
    headers = {'HTTP_INTERNAL_SERVICE_TOKEN': 'land-registry-internal-secret-2026',
      'HTTP_X_INTERNAL_SERVICE': 'true'}
    response = self.client.patch(self.unlock_url, **headers)
    self.assertEqual(response.status_code, 200)
    self.parcel.refresh_from_db(using=self.shard)
    self.assertEqual(self.parcel.status, 'available')
    self.assertEqual(response.data['detail'], 'the parcel is unlocked')

  def test_search_parcels_filtering(self):
    self.client.force_authenticate(user=self.user)
    url = f'{self.base_url}search/?min_size=400&max_size=600'
    with patch('common.permissions.LandPermission.has_permission', return_value=True), \
      patch('common.permissions.RegistrarPermission.has_permission', return_value=True):
      response = self.client.get(url)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(response.data), 1)
      self.assertEqual(response.data[0]['khasra_number'], 'KH-23')