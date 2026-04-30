from functools import wraps
from rest_framework.response import Response
from django.conf import settings

def internal_service(view_func):
  @wraps(view_func)
  def wrapper(self, request, *args, **kwargs):
    print(f'registry received headers: {dict(request.headers)}')
    print(f"token from header: '{request.headers.get('Internal-Service-Token')}'")
    print(f"expected secret: '{settings.INTERNAL_SERVICE_SECRET}'")
    token = request.headers.get('Internal-Service-Token')
    if not token:
      return Response({'err': 'the inter token is missing'}, status=403)
    if token != settings.INTERNAL_SERVICE_SECRET:
      print('tokens do not match')
      return Response({'err': 'the wrong inter token'}, status=403)
    return view_func(self, request, *args, **kwargs)
  return wrapper