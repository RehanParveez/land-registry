from rest_framework.test import APITestCase
from unittest.mock import MagicMock
import uuid

class RegistryParentTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.registrar = MagicMock()
    cls.registrar.username = 'registrar_user'
    cls.registrar.pk = uuid.uuid4()
    cls.citizen = MagicMock()
    cls.citizen.username = 'citizen_user'
    cls.citizen.pk = uuid.uuid4()

  @staticmethod
  def create_mock_topology_stack(province_name = 'Punjab'):
    mock_prov = MagicMock(name = 'Province')
    mock_prov.name = province_name
    mock_div = MagicMock(name = 'Division')
    mock_div.name = f'{province_name} Division'
    mock_div.province = mock_prov
    mock_dist = MagicMock(name = 'District')
    mock_dist.name = 'Lahore District'
    mock_dist.division = mock_div
    mock_teh = MagicMock(name = 'Tehsil')
    mock_teh.name = 'Raiwind'
    mock_teh.district = mock_dist
    mock_mauza = MagicMock(name = 'Mauza')
    mock_mauza.id = uuid.uuid4()
    mock_mauza.name = 'Mauza Khayaban'
    mock_mauza.tehsil = mock_teh
        
    return mock_prov, mock_div, mock_dist, mock_teh, mock_mauza