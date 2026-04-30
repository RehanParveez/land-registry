from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile
from rest_framework_simplejwt.tokens import RefreshToken

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