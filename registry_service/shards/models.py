from django.db import models
from common.models import BaseModel

class ParcelArea(BaseModel):
  parcel_uuid = models.UUIDField(unique=True, db_index=True)
  prov_code = models.CharField(max_length=30) 
    
  def __str__(self):
    return f'{self.parcel_uuid}'