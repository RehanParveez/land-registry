from shards.models import ParcelArea

class ShardIndexingService:
  @staticmethod
  def register_parcel(parcel_uuid, prov_code):
    new_area_rec = ParcelArea.objects.create(parcel_uuid=parcel_uuid, prov_code=prov_code)
    return new_area_rec

  @staticmethod
  def get_shard_for_parcel(parcel_uuid):
    parcel_exists = ParcelArea.objects.filter(parcel_uuid=parcel_uuid).exists()   
    if parcel_exists == True:
      rec = ParcelArea.objects.get(parcel_uuid=parcel_uuid)
      return rec.prov_code
        
    return None