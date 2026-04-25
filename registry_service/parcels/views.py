from rest_framework import viewsets, filters
from parcels.serializers import LandParcelSerializer
from parcels.models import LandParcel
from common.permissions import RegistrarPermission, CitizenPermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from parcels.services import ParcelLockService

class ParcelViewSet(viewsets.ModelViewSet):
  serializer_class = LandParcelSerializer
  queryset = LandParcel.objects.all()
  permission_classes = [RegistrarPermission | CitizenPermission]
  filter_backends = [DjangoFilterBackend, filters.SearchFilter]
  filterset_fields = ['status', 'land_use', 'mauza']
  search_fields = ['khasra_number']
    
  def get_queryset(self):
    return self.queryset.select_related('mauza').all()

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
    shard_name = kwargs.get('shard', 'default')
    success, message = ParcelLockService.acquire_lock(pk, shard_name)
    if not success:
      return Response({'detail': message}, status=400)  
    return Response({'detail': message}, status=200)