from django.db import models, transaction
from ownership.models import Title, Ledger

class TitleValidationService:
  @staticmethod
  def validate_shares(parcel_id, new_share=0, exclude_owner_uuid=None):
    curr_shares = Title.objects.filter(parcel_id=parcel_id)
    if exclude_owner_uuid:
      curr_shares = curr_shares.exclude(owner_uuid=exclude_owner_uuid)  
    tot_exist = curr_shares.aggregate(models.Sum('share_perc'))['share_perc__sum'] or 0
        
    if (tot_exist + new_share) > 100:
      return False, f'the sum of shares ({tot_exist + new_share}%) exceeds 100% limit'
    return True, 'Success'

class OwnershipService:
  @staticmethod
  def execute_transfer(parcel, from_uuid, to_uuid, share, price, ref):
    with transaction.atomic():
      title, created = Title.objects.get_or_create(parcel=parcel, owner_uuid=to_uuid, defaults={'share_perc': share})
      if not created:
        title.share_perc += share
        title.save()
      Ledger.objects.create(parcel=parcel, from_owner_uuid=from_uuid, to_owner_uuid=to_uuid, transaction_ref=ref, price=price)