import uuid
from topology.models import Province, Division, District, Tehsil, Mauza
from parcels.models import LandParcel

def create_land_hierarchy(shard_name, khasra = 'KH-23'):
  u_id = str(uuid.uuid4())[-4]
  province = Province.objects.using(shard_name).create(name = f'Province {shard_name}', code = f'PROV-{shard_name}', database_alias=shard_name)
  division = Division.objects.using(shard_name).create(name = 'Division-1', code = f'DIV-{shard_name} {u_id}', province=province)
  district = District.objects.using(shard_name).create(name = 'District-1', code = f'DIST-{shard_name} {u_id}', division=division)
  tehsil = Tehsil.objects.using(shard_name).create(name = 'Tehsil-1', code = f'TEH-{shard_name} {u_id}', district=district)
  mauza = Mauza.objects.using(shard_name).create(name = 'Mauza-1', code = f'MAU-{shard_name} {u_id}', tehsil=tehsil)
  parcel = LandParcel.objects.using(shard_name).create(mauza=mauza, khasra_number=khasra, square_footage=500.00, land_use = 'residential',status = 'available')
  return parcel, mauza