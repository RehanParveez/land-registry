from django.db import models, transaction
from ownership.models import Title, Ledger
from decimal import Decimal

class TitleValidationService:
  @staticmethod
  def validate_shares(parcel_id, new_share=0, exclude_owner_uuid=None, shard='default'):
    curr_shares = Title.objects.using(shard).filter(parcel_id=parcel_id)
    if exclude_owner_uuid:
      curr_shares = curr_shares.exclude(owner_uuid=exclude_owner_uuid)  
    tot_exist = curr_shares.aggregate(models.Sum('share_perc'))['share_perc__sum'] or 0
    
    new_share_dec = Decimal(str(new_share))
    if (tot_exist + new_share_dec) > 100:
      return False, f'the sum of shares ({tot_exist + new_share_dec}%) exceeds 100% limit'
    return True, 'Success'

class OwnershipService:
  @staticmethod
  def execute_transfer(parcel, from_uuid, to_uuid, share, price, ref, shard='default'):
    with transaction.atomic():
      title, created = Title.objects.using(shard).get_or_create(parcel=parcel, owner_uuid=to_uuid, defaults={'share_perc': share})
      if not created:
        title.share_perc += share
        title.save(using=shard)
      Ledger.objects.using(shard).create(parcel=parcel, from_owner_uuid=from_uuid, to_owner_uuid=to_uuid, transaction_ref=ref, price=price)