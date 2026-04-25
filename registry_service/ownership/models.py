from django.db import models
from common.models import BaseModel
from parcels.models import LandParcel

class Title(BaseModel):
  parcel = models.ForeignKey(LandParcel, on_delete=models.PROTECT, related_name = 'titles')
  owner_uuid = models.UUIDField(db_index=True)
  share_perc = models.DecimalField(max_digits=12, decimal_places=2)

  class Meta:
    unique_together = ('parcel', 'owner_uuid')

class Ledger(BaseModel):
  parcel = models.ForeignKey(LandParcel, on_delete=models.PROTECT, related_name = 'ledger_entries')
  from_owner_uuid = models.UUIDField(null=True, blank=True)
  to_owner_uuid = models.UUIDField()
  transaction_ref = models.CharField(max_length=100, unique=True)
  price = models.DecimalField(max_digits=14, decimal_places=2)

  def __str__(self):
    return f'{self.parcel.khasra_number}'