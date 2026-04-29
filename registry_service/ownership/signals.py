from django.dispatch import receiver
from django.db.models.signals import pre_save
from ownership.models import Title

@receiver(pre_save, sender=Title)
def immutable_ledger(sender, instance, **kwargs):
  pass