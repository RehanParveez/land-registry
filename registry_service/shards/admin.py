from django.contrib import admin
from shards.models import ParcelArea

@admin.register(ParcelArea)
class ParcelAreaAdmin(admin.ModelAdmin):
  list_display = ['id', 'parcel_uuid', 'prov_code', 'created_at', 'updated_at']