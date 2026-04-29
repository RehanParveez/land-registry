from celery import shared_task
from shards.models import ParcelArea
from parcels.models import LandParcel
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def shard_integrity():
  shards = ['punjab', 'sindh']
  missing_count = 0
  extra_count = 0
  report = []

  for shard in shards:
    in_map = set(ParcelArea.objects.filter(prov_code=shard).values_list('parcel_uuid', flat=True))
    in_db = set(LandParcel.objects.using(shard).values_list('id', flat=True))

    missing = in_map - in_db
    extra = in_db - in_map
    missing_count += len(missing)
    extra_count += len(extra)

    if missing:
      print(f'{shard} in map but not in db: {missing}')
      report.append(f'{shard} missing from db {len(missing)}')
    if extra:
      print(f'{shard} in db but not in map {extra}')
      report.append(f'{shard} not regist. in map {len(extra)}')
    if not missing and not extra:
      print(f'{shard} the integ check is passed')
      report.append(f'{shard}: clean')

  if missing_count > 0 or extra_count > 0:
    send_mail(subject='the issues are pres', message=' | '.join(report), from_email=settings.DEFAULT_FROM_EMAIL,
      recipient_list=[settings.EMAIL_HOST_USER], fail_silently=False)
    
  return f'{missing_count} extra {extra_count}'