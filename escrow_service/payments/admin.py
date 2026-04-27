from django.contrib import admin
from payments.models import Wallet, Payment

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
  list_display = ['id', 'agreement', 'balance', 'is_locked', 'created_at', 'updated_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
  list_display = ['id', 'wallet', 'amount', 'direction', 'status', 'transaction_id', 'created_at', 'updated_at']
