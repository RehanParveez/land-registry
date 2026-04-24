from rest_framework import serializers
from shards.models import ParcelArea

class GlobalParcelMapSerializer(serializers.ModelSerializer):
  class Meta:
    model = ParcelArea
    fields = ['id', 'parcel_uuid', 'prov_code', 'created_at', 'updated_at']  
    read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_prov_code(self, value):
      valid_codes = ['punjab', 'sindh']
      if value not in valid_codes:
        raise serializers.ValidationError('wrong province code')  
      return value