from django.contrib import admin
from contracts.models import Agreement

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
  list_display = ['id', 'parcel_id', 'buyer_uuid', 'seller_uuid', 'agreed_price', 'status', 'created_at', 'updated_at']


