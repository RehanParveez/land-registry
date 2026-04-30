from functools import wraps
from rest_framework.response import Response
from django.conf import settings

def internal_service(view_func):
  @wraps(view_func)
  def wrapper(self, request, *args, **kwargs):
    token = request.headers.get('Internal-Service-Token')
    if not token:
      return Response({'err': 'the inter token is missing'}, status=403)
    if token != settings.INTERNAL_SERVICE_SECRET:
      return Response({'err': 'the wrong inter token'}, status=403)
    return view_func(self, request, *args, **kwargs)
  return wrapper