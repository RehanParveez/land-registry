from rest_framework import viewsets, mixins, permissions
from accounts.serializers.detail import UserSerializer
from accounts.models import User
from common.permissions import RegistrarPermission
from rest_framework.decorators import action
from accounts.services import AuthService
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

class AuthenticationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
  serializer_class = UserSerializer
  queryset = User.objects.all()

  def get_queryset(self):
    if not self.request.user.is_authenticated:
      return self.queryset.none()  
    if self.request.user.control == 'registrar':
      return self.queryset
    return self.queryset.filter(id=self.request.user.id)

  def get_permissions(self):
    if self.action == 'register':
      return [permissions.AllowAny()]
    if self.action == 'list':
        return [RegistrarPermission()]
    if self.action == 'me':
      return [permissions.IsAuthenticated()]
  
    return [permissions.IsAuthenticated()]

  @action(detail=False, methods=['post'])
  def register(self, request):
    serializer = self.get_serializer(data=request.data)
        
    if serializer.is_valid():
      raw_cnic = request.data.get('cnic')
      user = AuthService.register_user(serializer.validated_data, raw_cnic)
      return Response(UserSerializer(user).data, status=201)
            
    return Response(serializer.errors, status=400)

  @action(detail=False, methods=['get'])
  def me(self, request):
    serializer = self.get_serializer(request.user)
    return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
  def post(self, request, *args, **kwargs):
    response = super().post(request, *args, **kwargs)
    if response.status_code == 200:
      email = request.data.get('email')
      fingerprint = request.headers.get('X-Device-Fingerprint', 'unknown_device')
      AuthService.register_device_by_email(email, fingerprint)

    return response