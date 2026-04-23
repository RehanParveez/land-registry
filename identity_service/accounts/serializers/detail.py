from rest_framework import serializers
from accounts.models import User, Profile
from identity_service.accounts.serializers.basic import ProfileSerializer1

class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = ['user', 'cnic_hash', 'full_name', 'is_verified', 'bio', 'phone', 'dob', 'address', 'pic']
    read_only_fields = ['is_verified', 'cnic_hash']

class UserSerializer(serializers.ModelSerializer):
  profile = ProfileSerializer1(read_only=True)
  cnic = serializers.CharField(write_only=True, required=False)

  class Meta:
    model = User
    fields = ['id', 'email', 'username', 'control', 'password', 'profile', 'cnic']
    extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True}}

  def create(self, validated_data):
    validated_data.pop('cnic', None)
    return User.objects.create_user(**validated_data)