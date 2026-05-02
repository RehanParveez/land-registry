from topology.models import Province, Division, District, Tehsil, Mauza
from parcels.models import LandParcel

def create_land_hierarchy(shard_name, khasra = 'KH-23'):
  province = Province.objects.using(shard_name).create(name = f'Province {shard_name}', code = f'PROV-{shard_name}', database_alias=shard_name)
  division = Division.objects.using(shard_name).create(name = 'Division-1', code = f'DIV-{shard_name}', province=province)
  district = District.objects.using(shard_name).create(name = 'District-1', code = f'DIST-{shard_name}', division=division)
  tehsil = Tehsil.objects.using(shard_name).create(name = 'Tehsil-1', code = f'TEH-{shard_name}', district=district)
  mauza = Mauza.objects.using(shard_name).create(name = 'Mauza-1', code = f'MAU-{shard_name}', tehsil=tehsil)
  parcel = LandParcel.objects.using(shard_name).create(mauza=mauza, khasra_number=khasra, square_footage=500.00, land_use = 'residential',status = 'available')
  return parcel, mauza