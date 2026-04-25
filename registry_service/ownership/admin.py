from django.contrib import admin
from ownership.models import Title, Ledger

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
  list_display = ['parcel', 'owner_uuid', 'share_perc', 'get_land_use', 'get_status', 'created_at', 'updated_at']
  
  @admin.display(description = 'Land Use')
  def get_land_use(self, obj):
    return obj.parcel.land_use

  @admin.display(description = 'Status')
  def get_status(self, obj):
    return obj.parcel.status

@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
  list_display = ['parcel', 'from_owner_uuid', 'to_owner_uuid', 'transaction_ref', 'price', 'created_at', 'updated_at']
