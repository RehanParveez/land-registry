import redis
import json
from django.http import JsonResponse

class UnchangedMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
    self.redis_client = redis.Redis(host='127.0.0.1', port=6379, db=1)

  def __call__(self, request):
    if request.method != 'POST':
      return self.get_response(request)
    unchanged_key = request.headers.get('Unchanged-Key')
    if not unchanged_key:
      return self.get_response(request)

    cache_key = f'unchanged:{unchanged_key}'
    cached = self.redis_client.get(cache_key)
    if cached:
      print(f'request blocked key: {unchanged_key}')
      cached_data = json.loads(cached)
      return JsonResponse(cached_data['body'], status=cached_data['status'], safe=False)

    response = self.get_response(request)
    if response.status_code in [200, 201]:
      cache_data = json.dumps({'body': json.loads(response.content), 'status': response.status_code})
      self.redis_client.setex(cache_key, 86400, cache_data)
      print(f'key cached: {unchanged_key}')

    return response