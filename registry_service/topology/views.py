from rest_framework import viewsets
from topology.serializers.detail import ProvinceTreeSerializer
from topology.models import Province
from common.permissions import CitizenPermission, RegistrarPermission 
from rest_framework.decorators import action
from rest_framework.response import Response

class TopologyViewSet(viewsets.ModelViewSet):
  serializer_class = ProvinceTreeSerializer
  queryset = Province.objects.all()
  permission_classes = [CitizenPermission | RegistrarPermission]
    
  def get_queryset(self):
    return self.queryset

  def get_serializer_class(self):
    if self.action == 'tree':
      return ProvinceTreeSerializer
    return self.serializer_class

  @action(detail=False, methods=['get'], url_path='tree')
  def tree(self, request, *args, **kwargs):
    provinces = self.get_queryset().prefetch_related('divisions__districts__tehsils__mauzas').all()
    serializer = self.get_serializer(provinces, many=True)
    return Response(serializer.data)