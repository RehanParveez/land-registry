from rest_framework import serializers
from accounts.models import Profile

class ProfileSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = ['full_name', 'is_verified']