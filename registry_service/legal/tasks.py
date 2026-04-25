from celery import shared_task
from django.utils import timezone
from legal.models import StayOrder, Charge
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def auto_expire_stays():
  shards = ['punjab', 'sindh']
  today = timezone.now().date()
    
  for shard in shards:
    expired_stays = StayOrder.objects.using(shard).filter(is_active=True, expiry_date__lt=today)
    
    for stay in expired_stays:
      stay.is_active = False
      stay.save(using=shard)     
      parcel = stay.parcel
      has_stays = StayOrder.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
      has_charges = Charge.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
            
      if not has_stays:
        if not has_charges:
          parcel.status = 'available'
          parcel.save(using=shard)
          subject = 'the stay order has expired'
          body = 'the parcel is avail'       
          send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], fail_silently=False)
    
  return 'the task is completed'