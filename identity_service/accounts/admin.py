from django.contrib import admin
from accounts.models import User, Profile, UserDevice

class ProfileInline(admin.StackedInline):
    model = Profile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  inlines = [ProfileInline]
  list_display = ['id', 'email', 'cnic', 'control', 'created_at', 'updated_at']
  
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'cnic_hash', 'full_name', 'is_verified', 'bio', 'phone', 'dob', 'address', 'pic', 'created_at', 'updated_at']

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
  list_display = ['id', 'device_fingerprint', 'is_trusted', 'last_login', 'created_at', 'updated_at']