import hashlib
from django.db import transaction
from accounts.models import User, Profile, UserDevice

class AuthService:
  @staticmethod
  def hash_cnic(raw_cnic):
    salt = 'land_registery'
    salted_cnic = f'{raw_cnic}{salt}'
    salted_cnic = salted_cnic.encode()
    return hashlib.sha256(salted_cnic).hexdigest()

  @staticmethod
  @transaction.atomic
  def register_user(validated_data, raw_cnic):
    user = User.objects.create_user(**validated_data)
    cnic_hash = AuthService.hash_cnic(raw_cnic)
    Profile.objects.create(user=user, cnic_hash=cnic_hash, full_name=user.username)
    return user

  @staticmethod
  def register_device_by_email(email, fingerprint):
    user = User.objects.filter(email=email).first()
    if user:
      device, created = UserDevice.objects.get_or_create(user=user, device_fingerprint=fingerprint)
      return device
            
    return None