from django.dispatch import receiver
from django.db.models.signals import post_save
from verification.models import VerificationRec

@receiver(post_save, sender=VerificationRec)
def update_profile(sender, instance, created, **kwargs):
  if instance.status == 'success':
    user_profile = instance.user.profile
    if user_profile.is_verified == False:
      user_profile.is_verified = True
      user_profile.save()
      print(f'{instance.user.email} is now verified')