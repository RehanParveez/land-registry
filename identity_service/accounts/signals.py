from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models import User
from user_sessions.models import ActiveSession

@receiver(post_save, sender=User)
def on_account_lock(sender, instance, created, **kwargs):
  if created:
    return
  if instance.is_active:
    return
  del_count, _ = ActiveSession.objects.filter(user=instance).delete()
  print(f'locked {instance.email} cleared {del_count}')