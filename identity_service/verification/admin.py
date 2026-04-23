from django.contrib import admin
from verification.models import VerificationRec

@admin.register(VerificationRec)
class VerificationRecAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'method', 'status', 'metadata', 'created_at', 'updated_at']
