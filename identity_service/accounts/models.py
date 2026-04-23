from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import BaseModel

class User(AbstractUser, BaseModel):
  CONTROL_CHOICES = (
    ('agent', 'Agent'), 
    ('citizen', 'Citizen'), 
    ('tehsildar', 'Tehsildar'),
    ('registrar', 'Registrar')  
  )
  email = models.EmailField(unique=True)
  cnic = models.CharField(max_length=16, unique=True, null=True, blank=True)
  control = models.CharField(max_length=40, choices=CONTROL_CHOICES, default = 'citizen')
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username', 'cnic']

class Profile(BaseModel):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profile')
  cnic_hash = models.CharField(max_length=65, null=True, blank=True)
  full_name = models.CharField(max_length=70, null=True, blank=True)
  is_verified = models.BooleanField(default=False)
  bio = models.TextField(null=True, blank=True)
  phone = models.CharField(max_length=35)
  dob = models.DateField(null=True, blank=True)
  address = models.CharField(max_length=100, null=True, blank=True)
  pic = models.ImageField(upload_to = 'profiles/', null=True, blank=True)
  
  def __str__(self):
    return f'{self.user.email}'

class UserDevice(BaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'devices')
  device_fingerprint = models.CharField(max_length=100)
  is_trusted = models.BooleanField(default=False)
  last_login = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f'{self.user.email}'