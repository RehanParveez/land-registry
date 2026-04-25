from rest_framework import serializers
from parcels.models import LandParcel

class LandParcelSerializer(serializers.ModelSerializer):
  mauza_name = serializers.ReadOnlyField(source = 'mauza.name')
  class Meta:
    model = LandParcel
    fields = ['id', 'mauza', 'mauza_name', 'khasra_number', 'square_footage', 'land_use', 'status', 'created_at', 'updated_at']
    read_only_fields = ['status', 'created_at', 'updated_at']