from rest_framework import serializers
from user_sessions.models import ActiveSession

class ActiveSessionSerializer(serializers.ModelSerializer):
  class Meta:
    model = ActiveSession
    fields = ['id', 'user', 'session_key', 'ip_address', 'user_agent', 'is_flagged', 'created_at', 'updated_at']
    read_only_fields = ['user', 'user_agent', 'session_key', 'created_at', 'updated_at']