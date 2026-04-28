from django.utils.deprecation import MiddlewareMixin
from sessions.models import ActiveSession
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout

class SessionHardeningMiddleware(MiddlewareMixin):
  def process_request(self, request):
    header = request.headers.get('Authorization')
    if header is not None:
      if header.startswith('Bearer '):
        authenticator = JWTAuthentication()
        auth_result = authenticator.authenticate(request)    
        if auth_result is not None:
          user, token = auth_result
          request.user = user
          
    if not request.user.is_authenticated:
      return None
    curr_ip = self.get_client_ip(request)
    corr_session_key = request.session.session_key or header
    if corr_session_key:
      corr_session_key = corr_session_key[:255]
    session_key = corr_session_key

    if not corr_session_key:
      return None
    act_session = ActiveSession.objects.filter(session_key=corr_session_key)
    act_session = act_session.first()

    if act_session:
      if act_session.ip_address != curr_ip:
       act_session.is_flagged = True
       act_session.save()
       logout(request)
  
       print(f'ip mismatch {request.user.email}')
       return None
   
    else:
      user_agent = request.META.get('HTTP_USER_AGENT', 'unknown') or 'unknown'
      ActiveSession.objects.create(user=request.user, session_key=corr_session_key, ip_address=curr_ip,
        user_agent=user_agent[:280])
      print(f'the rec is created for {request.user.email}')
    return None

  def get_client_ip(self, request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
      ip = x_forwarded.split(',')[0]
    else:
      ip = request.META.get('REMOTE_ADDR')
    return ip