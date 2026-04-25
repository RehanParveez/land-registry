from django.contrib import admin
from parcels.models import LandParcel

@admin.register(LandParcel)
class LandParcelAdmin(admin.ModelAdmin):
  list_display = ['mauza', 'khasra_number', 'square_footage', 'land_use', 'status', 'created_at', 'updated_at']
