from django.test import RequestFactory, TransactionTestCase
from shards.middleware import ProvinceRoutingMiddleware
from unittest.mock import patch, MagicMock
from shards.router import LandShardRouter, set_current_shard, clear_current_shard
import uuid  
from shards.services import ShardIndexingService
from topology.tests_utils import RegistryParentTestCase
from django.contrib.auth.models import User

class TestProvinceRoutingMiddleware(TransactionTestCase):
  databases = {'default', 'punjab', 'sindh'}
  def setUp(self):
    self.factory = RequestFactory()
    self.get_response = lambda req: None
    self.middleware = ProvinceRoutingMiddleware(self.get_response)

  @patch('shards.middleware.set_current_shard')
  @patch('shards.middleware.clear_current_shard')
  def test_routing_by_path_punjab(self, mock_clear, mock_set):
    request = self.factory.get('/punjab/parcels/') 
    self.middleware(request)
    mock_set.assert_called_with('punjab')
    self.assertTrue(mock_clear.called)

  @patch('shards.middleware.set_current_shard')
  def test_routing_by_path_sindh(self, mock_set):
    request = self.factory.get('/sindh/ownership/')
    self.middleware(request)
    mock_set.assert_called_with('sindh')

  @patch('shards.middleware.set_current_shard')
  def test_process_view_shard_kwargs(self, mock_set):
    request = self.factory.get('/punjab/topology/')
    view_kwargs = {'shard': 'punjab', 'id': 1}   
    response = self.middleware.process_view(request, None, None, view_kwargs)   
    mock_set.assert_called_with('punjab')
    self.assertNotIn('shard', view_kwargs)
    self.assertIsNone(response)

  @patch('shards.middleware.set_current_shard')
  def test_no_shard_in_path(self, mock_set):
    request = self.factory.get('/shards/shard/status/')
    self.middleware(request)
    mock_set.assert_not_called()
    
class TestLandShardRouter(TransactionTestCase):
  databases = {'default', 'punjab', 'sindh'}
  def setUp(self):
    self.router = LandShardRouter()
    clear_current_shard()

  def test_central_apps_always_use_default(self):
    mock_model = MagicMock()
    mock_model._meta.app_label = 'auth'
    set_current_shard('punjab')  
    db_read = self.router.db_for_read(mock_model)
    db_write = self.router.db_for_write(mock_model)  
    self.assertEqual(db_read, 'default')
    self.assertEqual(db_write, 'default')

  def test_topology_uses_current_shard(self):
    mock_model = MagicMock()
    mock_model._meta.app_label = 'topology' 
    set_current_shard('sindh')  
    db_read = self.router.db_for_read(mock_model)
    self.assertEqual(db_read, 'sindh')
    clear_current_shard()
    self.assertEqual(self.router.db_for_read(mock_model), 'default')

  def test_allow_migrate_logic(self):
    self.assertTrue(self.router.allow_migrate('default', 'shards'))
    self.assertFalse(self.router.allow_migrate('punjab', 'auth'))
    self.assertTrue(self.router.allow_migrate('punjab', 'topology'))

  def tearDown(self):
    clear_current_shard()
  
class TestShardIndexingService(TransactionTestCase):
  databases = {'default', 'punjab', 'sindh'}
  @patch('shards.models.ParcelArea.objects.create')
  def test_register_parcel_success(self, mock_create):
    test_uuid = uuid.uuid4()
    test_prov = 'punjab'
    mock_create.return_value = MagicMock(parcel_uuid=test_uuid, prov_code=test_prov)
    result = ShardIndexingService.register_parcel(test_uuid, test_prov)
    mock_create.assert_called_once_with(parcel_uuid=test_uuid, prov_code=test_prov)
    self.assertEqual(result.prov_code, 'punjab')

  @patch('shards.models.ParcelArea.objects.filter')
  def test_get_shard_for_parcel_exists(self, mock_filter):
    test_uuid = uuid.uuid4()
    mock_record = MagicMock()
    mock_record.prov_code = 'sindh'
    mock_filter.return_value.first.return_value = mock_record
    shard_name = ShardIndexingService.get_shard_for_parcel(test_uuid)
    self.assertEqual(shard_name, 'sindh')
    mock_filter.assert_called_once_with(parcel_uuid=test_uuid)

  @patch('shards.models.ParcelArea.objects.filter')
  def test_get_shard_for_parcel_not_found(self, mock_filter):
    mock_filter.return_value.first.return_value = False
    shard_name = ShardIndexingService.get_shard_for_parcel(uuid.uuid4())  
    self.assertIsNone(shard_name)
    
class TestShardViewSet(RegistryParentTestCase):
  databases = {'default', 'punjab', 'sindh'}
  
  def setUp(self):
    super().setUp()
    self.base_url = '/shards/shard/' 
    self.status_url = f'{self.base_url}status/'

  @patch('django.db.connections')
  def test_shard_status_report_all_online(self, mock_connections):
    self.client.force_authenticate(user=None, token=self.registrar_token)
    
    mock_conn_obj = MagicMock()
    mock_conn_obj.ensure_connection.return_value = None
    mock_connections.__getitem__.return_value = mock_conn_obj
    response = self.client.get(self.status_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['default'], 'Online')
    self.assertEqual(response.data['punjab'], 'Online')
    self.assertEqual(response.data['sindh'], 'Online')

  def test_list_parcel_areas_unauthorized(self):
    self.client.force_authenticate(user=None, token=self.citizen_token)
    response = self.client.get(self.base_url)
    self.assertEqual(response.status_code, 403)

  @patch('shards.views.connections')
  def test_shard_status_with_offline_db(self, mock_connections):
    self.client.force_authenticate(user=None, token=self.registrar_token)
    def side_effect(key):
      m = MagicMock()
      if key == 'punjab':
        m.ensure_connection.return_value = 'Connection Error'
      else:
        m.ensure_connection.return_value = None
      return m
    mock_connections.__getitem__.side_effect = side_effect
    response = self.client.get(self.status_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['punjab'], 'Offline')
    self.assertEqual(response.data['default'], 'Online')