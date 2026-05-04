from rest_framework import serializers
from payments.models import Wallet, Payment

class WalletSerializer(serializers.ModelSerializer):
  class Meta:
    model = Wallet
    fields = ['id', 'agreement', 'balance', 'is_locked', 'created_at', 'updated_at']
    read_only_fields = ['id', 'created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
  agreement_id = serializers.CharField(write_only=True)
  class Meta:
    model = Payment
    fields = ['id', 'wallet', 'amount', 'direction', 'status', 'transaction_id', 'agreement_id', 'created_at', 'updated_at']
    read_only_fields = ['id', 'wallet', 'status', 'direction', 'transaction_id', 'created_at', 'updated_at']