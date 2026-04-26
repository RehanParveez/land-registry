from django.db import models
from common.models import BaseModel

class Agreement(BaseModel):
  STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('funded', 'Funded'),
    ('verified', 'Verified'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
  )
  parcel_id = models.UUIDField(help_text = 'the UUID of the lanparcel from reg serv')
  buyer_uuid = models.UUIDField(help_text = 'the UUID of the buyer from iden serv')
  seller_uuid = models.UUIDField(help_text = 'the UUID of the seller from iden serv')
  agreed_price = models.DecimalField(max_digits=16, decimal_places=2)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default = 'draft')

  def __str__(self):
    return f'{self.id} | {self.status}'