from django.db import models
from common.models import BaseModel
from contracts.models import Agreement

class Wallet(BaseModel):
  agreement = models.OneToOneField(Agreement, on_delete=models.CASCADE, related_name = 'wallet')
  balance = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
  is_locked = models.BooleanField(default=False)

  def __str__(self):
    return f'{self.agreement.id}'

class Payment(BaseModel):
  DIRECTION_CHOICES = (
    ('in', 'In'), 
    ('out', 'Out')
  )
  
  STATUS_CHOICES = (
    ('pending', 'Pending'), 
    ('success', 'Success'), 
    ('failed', 'Failed')
  )
  wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name = 'records')
  amount = models.DecimalField(max_digits=16, decimal_places=2)
  direction = models.CharField(max_length=7, choices=DIRECTION_CHOICES)
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default = 'pending')
  transaction_id = models.CharField(max_length=100, unique=True, null=True)