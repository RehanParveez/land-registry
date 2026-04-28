from rest_framework import viewsets
from sessions.serializers.detail import ActiveSessionSerializer
from common.permissions import LandPermission
from sessions.models import ActiveSession
from rest_framework.decorators import action
from rest_framework.response import Response

class SessionViewSet(viewsets.ModelViewSet):
  serializer_class = ActiveSessionSerializer
  queryset = ActiveSession.objects.all()

  def get_permissions(self):
    return [LandPermission()]

  def get_queryset(self):
    control_role = self.request.auth.get('control')
    user_uuid = self.request.user_id
    if control_role == 'registrar':
      return self.queryset.all()
    return self.queryset.filter(user_id=user_uuid)

  @action(detail=False, methods=['get'])
  def active_sessions(self, request):
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)

  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    instance.delete()
    return Response({'message': 'the session has been terminated'}, status=204)