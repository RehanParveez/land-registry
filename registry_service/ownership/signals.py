from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from ownership.models import Title, Ledger
import redis
import json

@receiver(pre_save, sender=Title)
def immutable_ledger(sender, instance, **kwargs):
  pass

@receiver(post_save, sender=Ledger)
def on_title_transfer(sender, instance, created, **kwargs):
  if not created:
    return
  redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
  event = {
    'parcel_id': str(instance.parcel.id),
    'from_owner': str(instance.from_owner_uuid),
    'to_owner': str(instance.to_owner_uuid),
    'price': str(instance.price),
    'ref': instance.transaction_ref,
   }
  redis_client.xadd('title_transfers', event)
  print(f'title trans for {instance.parcel.khasra_number}')