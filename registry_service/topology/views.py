from rest_framework import viewsets
from topology.serializers.detail import ProvinceTreeSerializer
from topology.models import Province
from common.permissions import LandPermission, RegistrarPermission
from rest_framework.decorators import action
from rest_framework.response import Response
from topology.services import TopologyService

class TopologyViewSet(viewsets.ModelViewSet):
  serializer_class = ProvinceTreeSerializer
  queryset = Province.objects.all()
  permission_classes = [LandPermission, RegistrarPermission]
  
  def get_shard(self):
    path = self.request.path 
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    if first_segment in ['punjab', 'sindh']:
      return first_segment
    return 'default'
    
  def get_queryset(self):
    return self.queryset.using(self.get_shard())

  def get_serializer_class(self):
    if self.action == 'tree':
      return ProvinceTreeSerializer
    return self.serializer_class
  
  def perform_create(self, serializer):
    shard = self.get_shard()
    instance = serializer.save()
    instance.save(using=shard)

  @action(detail=False, methods=['get'], url_path='tree')
  def tree(self, request, *args, **kwargs):
    shard = self.get_shard()
    provinces = self.get_queryset().using(shard).prefetch_related('divisions__districts__tehsils__mauzas').all()
    serializer = self.get_serializer(provinces, many=True)
    return Response(serializer.data)
  
  @action(detail=False, methods=['get'])
  def breadcrumb(self, request, *args, **kwargs):
    mauza_id = request.query_params.get('mauza_id')
    if not mauza_id:
      return Response({'err': 'the mauza_id is need.'}, status=400)
    result = TopologyService.get_location_breadcrumb(mauza_id, shard=self.get_shard())
    return Response({'breadcrumb': result})