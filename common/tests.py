from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from identity_service.accounts.models import Profile
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from unittest.mock import MagicMock
import uuid

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
  
  @staticmethod
  def create_mock_topology_stack(province_name = 'Punjab'):
    mock_prov = MagicMock(name = 'Province')
    mock_prov.name = province_name  
    mock_div = MagicMock(name = 'Division')
    mock_div.name = f'{province_name} Division'
    mock_div.province = mock_prov   
    mock_dist = MagicMock(name = 'District')
    mock_dist.name = 'Lahore District'
    mock_dist.division = mock_div
    mock_teh = MagicMock(name = 'Tehsil')
    mock_teh.name = 'Raiwind'
    mock_teh.district = mock_dist
    mock_mauza = MagicMock(name = 'Mauza')
    mock_mauza.id = uuid.uuid4()
    mock_mauza.name = 'Mauza Khayaban'
    mock_mauza.tehsil = mock_teh
        
    return mock_prov, mock_div, mock_dist, mock_teh, mock_mauza

  def get_token(self, user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

  def auth_headers(self, user):
    return {'HTTP_AUTHORIZATION': f'Bearer {self.get_token(user)}'}

  def test_check(self):
    self.assertEqual(self.registrar.username, 'registrar_user')
    self.assertEqual(self.citizen.username, 'citizen_user')
    self.assertEqual(self.tehsildar.username, 'teh_user')