from rest_framework import serializers
from ownership.models import Title, Ledger

class TitleSerializer(serializers.ModelSerializer):
  khasra_number = serializers.ReadOnlyField(source='parcel.khasra_number')
  acquisition_type = serializers.CharField(write_only=True, required=False, default = 'purchase')
  class Meta:
    model = Title
    fields = ['id', 'parcel', 'khasra_number', 'owner_uuid', 'share_perc', 'acquisition_type', 'created_at', 'updated_at']
    read_only_fields = ['created_at', 'updated_at']

class LedgerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Ledger
    fields = ['id', 'parcel', 'from_owner_uuid', 'to_owner_uuid', 'transaction_ref', 'price', 'created_at', 'updated_at']
    read_only_fields = ['created_at', 'updated_at']