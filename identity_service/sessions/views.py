from rest_framework import viewsets
from sessions.serializers.detail import ActiveSessionSerializer
from common.permissions import CitizenPermission, RegistrarPermission
from sessions.models import ActiveSession
from rest_framework.decorators import action
from rest_framework.response import Response

class SessionViewSet(viewsets.ModelViewSet):
  serializer_class = ActiveSessionSerializer
  queryset = ActiveSession.objects.all()

  def get_permissions(self):
    user = self.request.user
    if not user:
      return [CitizenPermission()]
    if not user.is_authenticated:
      return [CitizenPermission()]
  
    if user.control == 'registrar':
      return [RegistrarPermission()]
    return [CitizenPermission()]

  def get_queryset(self):
    user = self.request.user
    if user.control == 'registrar':
      return self.queryset
    return self.queryset.filter(user=user)

  @action(detail=False, methods=['get'])
  def active_sessions(self, request):
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)

  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    instance.delete()
    return Response({'message': 'the session has been terminated'}, status=204)