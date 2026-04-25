from django.db import models
from common.models import BaseModel
from parcels.models import LandParcel

class StayOrder(BaseModel):
  parcel = models.ForeignKey(LandParcel, on_delete=models.PROTECT, related_name = 'stay_orders')
  description = models.TextField(null=True, blank=True)
  court_name = models.CharField(max_length=200)
  case_num = models.CharField(max_length=100)
  issue_date = models.DateField()
  expiry_date = models.DateField()
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ['-issue_date']

  def __str__(self):
    return f'{self.parcel.khasra_number}'

class Charge(BaseModel):
  CURRENCY_CHOICES = (
    ('pkr', 'PKR'),
    ('usd', 'USD'),
    ('gbp', 'GBP'),
    ('eur', 'EUR'),
  )
  parcel = models.ForeignKey(LandParcel, on_delete=models.PROTECT, related_name = 'charges')
  bank_name = models.CharField(max_length=200)
  loan_acc_num = models.CharField(max_length=100)
  loan_amount = models.DecimalField(max_digits=14, decimal_places=2)
  currency = models.CharField(max_length=15, choices=CURRENCY_CHOICES, default = 'pkr') 
  registration_date = models.DateField(auto_now_add=True)
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return f'{self.parcel.khasra_number}'