from django.dispatch import receiver
from django.db.models.signals import pre_save
from ownership.models import Title
from django.core.exceptions import PermissionDenied

@receiver(pre_save, sender=Title)
def immutable_ledger(sender, instance, **kwargs):
  if instance.parcel.status == 'locked':
    raise PermissionDenied(f'{instance.parcel.khasra_number} is locked')