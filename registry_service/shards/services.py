from shards.models import ParcelArea

class ShardIndexingService:
  @staticmethod
  def register_parcel(parcel_uuid, prov_code):
    new_area_rec = ParcelArea.objects.create(parcel_uuid=parcel_uuid, prov_code=prov_code)
    return new_area_rec

  @staticmethod
  def get_shard_for_parcel(parcel_uuid):
    record = ParcelArea.objects.filter(parcel_uuid=parcel_uuid).first()   
    if record:
      return record.prov_code
    else:   
      return None