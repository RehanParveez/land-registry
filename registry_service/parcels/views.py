from rest_framework import viewsets, filters
from parcels.serializers import LandParcelSerializer
from parcels.models import LandParcel
from common.permissions import LandPermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from parcels.services import ParcelLockService

class ParcelViewSet(viewsets.ModelViewSet):
  serializer_class = LandParcelSerializer
  queryset = LandParcel.objects.all()
  permission_classes = [LandPermission]
  filter_backends = [DjangoFilterBackend, filters.SearchFilter]
  filterset_fields = ['status', 'land_use', 'mauza']
  search_fields = ['khasra_number']
  
  def get_shard(self):
    path = self.request.path
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    if first_segment in ['punjab', 'sindh']:
      return first_segment
    return 'default'
    
  def get_queryset(self):
    return self.queryset.using(self.get_shard()).select_related('mauza').all()
  
  def perform_create(self, serializer):
    shard = self.get_shard()
    instance = serializer.save()
    instance.save(using=shard)

  @action(detail=False, methods=['get'], url_path='search')
  def search_parcels(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    min_size = request.query_params.get('min_size')
    max_size = request.query_params.get('max_size')

    if min_size:
      queryset = queryset.filter(square_footage__gte=min_size)
    if max_size:
      queryset = queryset.filter(square_footage__lte=max_size)
    queryset = self.filter_queryset(queryset)
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)

  @action(detail=True, methods=['patch'])
  def lock(self, request, pk=None, *args, **kwargs):
    shard_name = self.get_shard()
    success, message = ParcelLockService.acquire_lock(pk, shard_name)
    if not success:
      return Response({'detail': message}, status=400)  
    return Response({'detail': message}, status=200)
  
  @action(detail=True, methods=['patch'])
  def unlock(self, request, pk=None, *args, **kwargs):
    shard_name = self.get_shard()
    success, message = ParcelLockService.release_lock(pk, shard_name)  
    if not success:
      return Response({'detail': message}, status=400)       
    return Response({'detail': message}, status=200)