from rest_framework import serializers
from contracts.models import Agreement

class AgreementSerializer(serializers.ModelSerializer):
  class Meta:
    model = Agreement
    fields = ['id', 'parcel_id', 'seller_uuid', 'agreed_price', 'status', 'created_at', 'updated_at']
    read_only_fields = ['id', 'status', 'created_at', 'updated_at']