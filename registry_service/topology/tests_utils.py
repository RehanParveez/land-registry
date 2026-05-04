from rest_framework.test import APITestCase
from unittest.mock import MagicMock
import uuid
from topology.models import Province, Division, District, Tehsil, Mauza

class RegistryParentTestCase(APITestCase):
  databases = {'default', 'punjab', 'sindh'}
  def setUp(self):
    self.registrar_uuid = str(uuid.uuid4())
    self.registrar_token = {'control': 'registrar', 'user_id': self.registrar_uuid}
    self.citizen_uuid = str(uuid.uuid4())
    self.citizen_token = {'control': 'citizen', 'user_id': self.citizen_uuid}
  
  @staticmethod
  def create_mock_topology_stack(shard = 'punjab'):
    prov = Province.objects.using(shard).create(name = 'Punjab', code = 'PUN-05', database_alias=shard)
    div = Division.objects.using(shard).create(name = 'Lahore Division', province=prov)
    dist = District.objects.using(shard).create(name = 'Lahore District', division=div)
    teh = Tehsil.objects.using(shard).create(name = 'Raiwind', district=dist)
    mauza = Mauza.objects.using(shard).create(name = 'Mauza Khayaban', tehsil=teh)
        
    return prov, div, dist, teh, mauza