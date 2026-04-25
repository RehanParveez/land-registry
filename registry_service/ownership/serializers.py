from rest_framework import serializers
from ownership.models import Title, Ledger

class TitleSerializer(serializers.ModelSerializer):
  khasra_number = serializers.ReadOnlyField(source='parcel.khasra_number')
  class Meta:
    model = Title
    fields = ['parcel', 'khasra_number', 'owner_uuid', 'share_perc', 'created_at', 'updated_at']

class LedgerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Ledger
    fields = ['parcel', 'from_owner_uuid', 'to_owner_uuid', 'transaction_ref', 'price', 'created_at', 'updated_at']