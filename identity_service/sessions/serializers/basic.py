from rest_framework import serializers
from sessions.models import ActiveSession

class ActiveSessionSerializer1(serializers.ModelSerializer):
  class Meta:
    model = ActiveSession
    fields = ['id', 'ip_address', 'is_flagged']