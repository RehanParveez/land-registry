from django.test import TransactionTestCase
from topology.models import Province, Division, District, Tehsil, Mauza
from topology.services import TopologyService
import uuid
from unittest.mock import patch
from topology.tests_utils import RegistryParentTestCase 
from django.urls import reverse

class TestTopologyBreadcrumb(TransactionTestCase):
  databases = {'default', 'punjab', 'sindh'}

  def setUp(self):
    self.prov = Province.objects.using('punjab').create(name = 'Punjab', code = 'PUN-01', database_alias = 'punjab')
    self.div = Division.objects.using('punjab').create(name = 'Lahore', code = 'LAH-DIV', province=self.prov)
    self.dist = District.objects.using('punjab').create(name = 'Lahore District', code = 'LAH-DIST', division=self.div)
    self.teh = Tehsil.objects.using('punjab').create(name = 'Raiwind', code = 'RAI-TEH', district=self.dist)
    self.mauza = Mauza.objects.using('punjab').create(name = 'Mauza Khayaban', code = 'KHY-MAUZA', tehsil=self.teh)

  def test_get_location_breadcrumb_right_id(self):
    expected = 'Punjab > Lahore > Lahore District > Raiwind > Mauza Khayaban'
    result = TopologyService.get_location_breadcrumb(self.mauza.id, shard = 'punjab')
    self.assertEqual(result, expected)

  def test_get_location_breadcrumb_wrong_id(self):
    random_uuid = uuid.uuid4()
    result = TopologyService.get_location_breadcrumb(random_uuid, shard = 'punjab')
    self.assertEqual(result, 'the location is not pres')

  def test_get_location_breadcrumb_database_shard(self):
    result = TopologyService.get_location_breadcrumb(self.mauza.id, shard = 'default')
    self.assertEqual(result, 'the location is not pres')
    res_correct = TopologyService.get_location_breadcrumb(self.mauza.id, shard = 'punjab')
    self.assertIn('Punjab', res_correct)
    
class TestTopologyViewSet(RegistryParentTestCase):
  @patch('topology.services.TopologyService.get_location_breadcrumb')
  def test_breadcrumb_action_success(self, mock_service):
    _, _, _, _, mock_mauza = self.create_mock_topology_stack(shard = 'punjab')
    expected_breadcrumb = 'Punjab > Lahore Division > Lahore District > Raiwind > Mauza Khayaban'
    mock_service.return_value = expected_breadcrumb
    url = reverse('topology-breadcrumb', kwargs={'shard': 'punjab'})
    self.client.force_authenticate(user=None, token=self.registrar_token)
    response = self.client.get(url, {'mauza_id': str(mock_mauza.id)})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['breadcrumb'], expected_breadcrumb)
    mock_service.assert_called_once_with(str(mock_mauza.id), shard = 'punjab')

  def test_breadcrumb_missing_id(self): 
    url = reverse('topology-breadcrumb', kwargs = {'shard': 'punjab'})
    self.client.force_authenticate(user=None, token=self.registrar_token)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data['err'], 'the mauza_id is need.')

  def test_tree_action_unauthorized(self):
    url = reverse('topology-tree', kwargs={'shard': 'punjab'})
    self.client.force_authenticate(user=None, token=self.citizen_token)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)