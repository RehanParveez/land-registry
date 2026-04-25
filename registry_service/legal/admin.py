from django.contrib import admin
from legal.models import StayOrder, Charge

@admin.register(StayOrder)
class StayOrderAdmin(admin.ModelAdmin):
  list_display = ['parcel', 'description', 'court_name', 'case_num', 'issue_date', 'expiry_date', 'is_active', 'created_at', 'updated_at']
  
@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
  list_display = ['parcel', 'bank_name', 'loan_acc_num', 'loan_amount', 'currency', 'registration_date', 'is_active', 'created_at', 'updated_at']

