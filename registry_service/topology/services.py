from topology.models import Mauza

class TopologyService:
  @staticmethod
  def get_location_breadcrumb(mauza_id, shard = 'default'):
    exists = Mauza.objects.using(shard).filter(id=mauza_id).exists()
        
    if exists:
      mauza = Mauza.objects.using(shard).select_related('tehsil__district__division__province').get(id=mauza_id)
      levels = [mauza.tehsil.district.division.province.name, mauza.tehsil.district.division.name, mauza.tehsil.district.name, mauza.tehsil.name, mauza.name]
      return " > ".join(levels)
    return 'the location is not pres'