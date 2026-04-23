from rest_framework import serializers
from verification.models import VerificationRec

class VerificationRecSerializer(serializers.ModelSerializer):
  class Meta:
    model = VerificationRec
    fields = ['id', 'method', 'status', 'metadata', 'created_at', 'updated_at']
    read_only_fields = ['status', 'metadata', 'created_at', 'updated_at']