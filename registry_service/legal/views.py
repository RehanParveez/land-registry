from rest_framework import viewsets
from legal.serializers import StayOrderSerializer, ChargeSerializer
from legal.models import StayOrder, Charge
from common.permissions import LandPermission
from rest_framework.decorators import action
from rest_framework.response import Response
from ownership.models import Title

class StayOrderViewSet(viewsets.ModelViewSet):
  serializer_class = StayOrderSerializer
  queryset = StayOrder.objects.all()
  permission_classes = [LandPermission]
  
  def get_shard(self):
    path = self.request.path
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    if first_segment in ['punjab', 'sindh']:
      return first_segment
    return 'default'

  def get_queryset(self):
    control_role = self.request.auth.get('control')
    user_uuid = self.request.user_id
    queryset = self.queryset.using(self.get_shard()).select_related('parcel')
    
    if control_role in ['registrar', 'tehsildar']:
      return queryset
    owned_parcel_ids = Title.objects.using(self.get_shard()).filter(owner_uuid=user_uuid).values_list('parcel_id', flat=True)
    return queryset.filter(parcel_id__in=owned_parcel_ids)
    
  @action(detail=False, methods=['post'])
  def apply_stay(self, request):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'the stay order is applied'}, status=201)
    return Response(serializer.errors, status=400)
  
  @action(detail=True, methods=['post'])
  def release_stay(self, request, pk=None, shard=None):
    stay = self.get_object()
    stay.is_active = False
    shard = self.get_shard()
    stay.save(using=shard)
    parcel = stay.parcel  
    other_stays = StayOrder.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
    active_charges = Charge.objects.using(shard).filter(parcel=parcel, is_active=True).exists()

    if not other_stays:
      if not active_charges:
        parcel.status = 'available'
        parcel.save(using=shard)
        return Response({'message': 'the land is now available'}, status=200)

    return Response({'message': 'the stay is rel but land remains locked'}, status=200)

class ChargeViewSet(viewsets.ModelViewSet):
  serializer_class = ChargeSerializer
  queryset = Charge.objects.all()
  permission_classes = [LandPermission]
  
  def get_shard(self):
    path = self.request.path
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    if first_segment in ['punjab', 'sindh']:
        return first_segment
    return 'default'

  def get_queryset(self):
    control_role = self.request.auth.get('control')
    user_uuid = self.request.user_id
    queryset = self.queryset.using(self.get_shard()).select_related('parcel').all()
    if control_role in ['registrar', 'tehsildar']:
      return queryset
    if control_role == 'agent':
      return queryset
    if control_role == 'citizen':
      owned_parcel_ids = Title.objects.using(self.get_shard()).filter(owner_uuid=user_uuid).values_list('parcel_id', flat=True)
      return queryset.filter(parcel_id__in=owned_parcel_ids)
        
    return queryset.none()

  @action(detail=False, methods=['post'])
  def apply_charge(self, request):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'the charge is registered'}, status=201)
    return Response(serializer.errors, status=400)
  
  @action(detail=True, methods=['post'])
  def release_charge(self, request, pk=None, shard=None):
    charge = self.get_object()
    charge.is_active = False
    shard = self.get_shard()
    charge.save(using=shard)
    parcel = charge.parcel
    active_stays = StayOrder.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
    other_charges = Charge.objects.using(shard).filter(parcel=parcel, is_active=True).exists()

    if not active_stays:
      if not other_charges:
        parcel.status = 'available'
        parcel.save(using=shard)
        return Response({'message': 'the land is now available'}, status=200)

    return Response({'message': 'the charge is rel but land remains locked'}, status=200)