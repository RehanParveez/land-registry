from django.contrib import admin
from user_sessions.models import ActiveSession

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'session_key', 'ip_address', 'user_agent', 'is_flagged', 'created_at', 'updated_at']

