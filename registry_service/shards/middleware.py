from shards.router import set_current_shard, clear_current_shard

class ProvinceRoutingMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    path_parts = request.path.strip('/').split('/')
        
    if 'punjab' in path_parts:
      set_current_shard('punjab')
    elif 'sindh' in path_parts:
      set_current_shard('sindh')
            
    resp = self.get_response(request)
    clear_current_shard()
    return resp