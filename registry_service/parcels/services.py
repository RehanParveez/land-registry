from django.core.cache import cache
from django.db import transaction
from parcels.models import LandParcel

class ParcelLockService:
  @staticmethod
  def acquire_lock(parcel_id, shard_name, duration=1800):
    lock_key = f'lock:parcel:{shard_name}:{parcel_id}'
    if cache.get(lock_key):
      return False, 'the parcel is curr locked'

    with transaction.atomic(using=shard_name):
      parcel = LandParcel.objects.using(shard_name).select_for_update().get(id=parcel_id)
      if parcel.status != 'available':
        return False, 'the parcel is not avail'
      parcel.status = 'locked'
      parcel.save(using=shard_name)
      cache.set(lock_key, 'locked', timeout=duration)
    return True, 'the parcel is locked for 30 mins'

  @staticmethod
  def release_lock(parcel_id, shard_name):
    lock_key = f'lock:parcel:{shard_name}:{parcel_id}'
    parcel = LandParcel.objects.using(shard_name).get(id=parcel_id)
    parcel.status = 'available'
    parcel.save(using=shard_name)
    cache.delete(lock_key)
    return True, 'the parcel is unlocked'