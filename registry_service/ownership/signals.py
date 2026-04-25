from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from ownership.models import Title, Ledger
from django.core.exceptions import PermissionDenied

@receiver(pre_save, sender=Title)
def immutable_ledger(sender, instance, **kwargs):
  if instance.parcel.status == 'locked':
    raise PermissionDenied(f'{instance.parcel.khasra_number} is locked')

@receiver(post_save, sender=Title)
def create_ledger_entry(sender, instance, created, **kwargs):
  if created:
    last_entry = Ledger.objects.using(instance._state.db).filter(parcel=instance.parcel).order_by('-created_at')
    last_entry = last_entry.first()
    previous_owner = last_entry.to_owner_uuid if last_entry else None
    Ledger.objects.using(instance._state.db).create(parcel=instance.parcel, from_owner_uuid=previous_owner, to_owner_uuid=instance.owner_uuid,
      transaction_ref=f'REG-{instance.id.hex[:8].upper()}', price=0.00)