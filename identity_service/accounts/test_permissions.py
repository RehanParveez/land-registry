from accounts.tests import ParentTestCase
from rest_framework.test import APIRequestFactory
from common.permissions import EnoughEscrowPermission, IdentityPermission, RegistrarPermission, LandPermission
from unittest.mock import patch 
from unittest.mock import MagicMock
from decimal import Decimal
from rest_framework.request import Request

class TestEscrowPermission(ParentTestCase):
  def setUp(self):
    self.factory = APIRequestFactory()
    self.perm = EnoughEscrowPermission()
  
  @patch('django.apps.apps.get_model')
  def test_sufficient_funds(self, mock_get_model):
    mock_wallet = MagicMock()
    mock_wallet.balance = Decimal('100000.00')
    mock_wallet.agreement.agreed_price = Decimal('95000.00')
    mock_get_model.return_value.objects.filter.return_value.first.return_value = mock_wallet
    raw_request = self.factory.post('/process/transfer/', {'agreement_id': 'some-uuid'}, format = 'json')
    request = Request(raw_request) 
    request._full_data = {'agreement_id': 'some-uuid'}
    result = self.perm.has_permission(request, None)
    self.assertTrue(result)
    print('enough funds')

  @patch('django.apps.apps.get_model')
  def test_insufficient_funds(self, mock_get_model):
    mock_wallet = MagicMock()
    mock_wallet.balance = Decimal('5000.00')
    mock_wallet.agreement.agreed_price = Decimal('10000.00')
    mock_get_model.return_value.objects.filter.return_value.first.return_value = mock_wallet
    raw_request = self.factory.post('/process/transfer/')
    request = Request(raw_request) 
    request._full_data = {'agreement_id': 'some-uuid'}
    result = self.perm.has_permission(request, None)
    self.assertFalse(result)
    print('not enough funds')
    
class TestIdentityAndRegistrar(ParentTestCase):
  def setUp(self):
    self.factory = APIRequestFactory()

  def test_identity_permission(self):
    perm = IdentityPermission()
    self.citizen.profile.is_verified = True
    self.citizen.profile.save()
    request = self.factory.get('/')
    request.user = self.citizen
    self.assertTrue(perm.has_permission(request, None))
    self.citizen.profile.is_verified = False
    self.citizen.profile.save()
    self.assertFalse(perm.has_permission(request, None))

  def test_registrar_permission(self):
    perm = RegistrarPermission()
    request = self.factory.get('/')
    self.assertTrue(perm.has_permission(request, None))
    raw_request = self.factory.post('/')
    request = Request(raw_request)
    request.auth = {'control': 'citizen'}
    self.assertFalse(perm.has_permission(request, None))
    
class TestLandPermission(ParentTestCase):
  def setUp(self):
    self.factory = APIRequestFactory()
    self.perm = LandPermission()

  def test_land_global_permission(self):
    raw_request = self.factory.get('/')
    request = Request(raw_request)
    request.auth = {'control': 'registrar', 'user_id': self.registrar.id}
    self.assertTrue(self.perm.has_permission(request, None))
    request.auth = None
    self.assertFalse(self.perm.has_permission(request, None))

  def test_land_object_ownership(self):
    MockLand = type('Land', (object,), {'owner_uuid': str(self.citizen.id)})
    land_obj = MockLand()
    raw_request = self.factory.get('/')
    request = Request(raw_request)
    request.auth = {'control': 'citizen', 'user_id': str(self.citizen.id)}
    self.perm.has_permission(request, None) 
    self.assertTrue(self.perm.has_object_permission(request, None, land_obj))
    request.auth = {'control': 'tehsildar', 'user_id': str(self.tehsildar.id)}
    self.perm.has_permission(request, None)
    self.assertFalse(self.perm.has_object_permission(request, None, land_obj))
    request.auth = {'control': 'registrar', 'user_id': str(self.registrar.id)}
    self.perm.has_permission(request, None)
    self.assertTrue(self.perm.has_object_permission(request, None, land_obj))