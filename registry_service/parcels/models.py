from django.db import models
from common.models import BaseModel

class LandParcel(BaseModel):
  STATUS_CHOICES = (
    ('available', 'Available'),
    ('locked', 'Locked'),        
    ('pending', 'Pending'), 
  )
    
  USAGE_CHOICES = (
    ('residential', 'Residential'),
    ('commercial', 'Commercial'),
    ('agricultural', 'Agricultural'),
  )
  mauza = models.ForeignKey('topology.Mauza', on_delete=models.PROTECT, related_name = 'parcels')
  khasra_number = models.CharField(max_length=100, db_index=True)
  square_footage = models.DecimalField(max_digits=12, decimal_places=2)
  land_use = models.CharField(max_length=25, choices=USAGE_CHOICES)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default = 'available')
    
  class Meta:
    unique_together = ('mauza', 'khasra_number')

  def __str__(self):
    return f'{self.khasra_number}'