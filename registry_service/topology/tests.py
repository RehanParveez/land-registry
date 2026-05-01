from django.test import TestCase
from topology.models import Province, Division, District, Tehsil, Mauza
from topology.services import TopologyService
import uuid
from unittest.mock import patch
from topology.tests_utils import RegistryParentTestCase 
from django.urls import reverse

class TestTopologyBreadcrumb(TestCase):
  @classmethod
  def setUpTestData(cls):
    cls.prov = Province.objects.create(name = 'Punjab', code = 'PUN-01', database_alias = 'punjab')
    cls.div = Division.objects.create(name = 'Lahore', code = 'LAH-DIV', province=cls.prov)
    cls.dist = District.objects.create(name = 'Lahore District', code = 'LAH-DIST', division=cls.div)
    cls.teh = Tehsil.objects.create(name = 'Raiwind', code = 'RAI-TEH', district=cls.dist)
    cls.mauza = Mauza.objects.create(name = 'Mauza Khayaban', code = 'KHY-MAUZA', tehsil=cls.teh)

  def test_get_location_breadcrumb_right_id(self):
    expected = 'Punjab > Lahore > Lahore District > Raiwind > Mauza Khayaban'
    result = TopologyService.get_location_breadcrumb(self.mauza.id)
    self.assertEqual(result, expected)

  def test_get_location_breadcrumb_wrong_id(self):
    random_uuid = uuid.uuid4()
    result = TopologyService.get_location_breadcrumb(random_uuid)
    self.assertEqual(result, 'the location is not pres')

  def test_get_location_breadcrumb_database_shard(self):
    result = TopologyService.get_location_breadcrumb(self.mauza.id, shard = 'default')
    self.assertIn('Punjab', result)
    
class TestTopologyViewSet(RegistryParentTestCase):
  @patch('common.permissions.LandPermission.has_permission')
  @patch('common.permissions.RegistrarPermission.has_permission')
  @patch('topology.services.TopologyService.get_location_breadcrumb')
  def test_breadcrumb_action_success(self, mock_service, mock_reg, mock_land):
    mock_land.return_value = True
    mock_reg.return_value = True
    _, _, _, _, mock_mauza = self.create_mock_topology_stack()
    expected_breadcrumb = 'Punjab > Lahore Division > Lahore District > Raiwind > Mauza Khayaban'
    mock_service.return_value = expected_breadcrumb
    url = reverse('topology-breadcrumb', kwargs={'shard': 'punjab'})
    self.client.force_authenticate(user=self.registrar)
    response = self.client.get(url, {'mauza_id': str(mock_mauza.id)})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['breadcrumb'], expected_breadcrumb)
    mock_service.assert_called_once_with(str(mock_mauza.id), shard = 'punjab')

  @patch('common.permissions.LandPermission.has_permission')
  @patch('common.permissions.RegistrarPermission.has_permission')
  def test_breadcrumb_missing_id(self, mock_reg, mock_land):
    mock_land.return_value = True
    mock_reg.return_value = True  
    url = reverse('topology-breadcrumb', kwargs = {'shard': 'punjab'})
    self.client.force_authenticate(user=self.registrar)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data['err'], 'the mauza_id is need.')

  @patch('common.permissions.LandPermission.has_permission')
  @patch('common.permissions.RegistrarPermission.has_permission')
  def test_tree_action_unauthorized(self, mock_reg, mock_land):
    mock_land.return_value = True
    mock_reg.return_value = False
    url = reverse('topology-tree', kwargs={'shard': 'punjab'})
    self.client.force_authenticate(user=self.citizen)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)