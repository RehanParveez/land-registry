from django.test import RequestFactory, TestCase
from shards.middleware import ProvinceRoutingMiddleware
from unittest.mock import patch

class TestProvinceRoutingMiddleware(TestCase):
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