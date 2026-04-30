from rest_framework import viewsets, mixins, serializers
from ownership.serializers import TitleSerializer, LedgerSerializer
from ownership.models import Title, Ledger
from common.permissions import LandPermission, RegistrarPermission
from legal.models import StayOrder, Charge
import uuid
from django.db.models import Q
from ownership.services import TitleValidationService
from rest_framework.permissions import AllowAny

class TitleViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
  serializer_class = TitleSerializer
  queryset = Title.objects.all()
  permission_classes = [LandPermission, RegistrarPermission]
  
  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    if not serializer.is_valid():
      print(f'serializer error: {serializer.errors}')
    return super().create(request, *args, **kwargs)
  
  def get_permissions(self):
    if self.action == 'create':
      return [AllowAny()]
    perm_instances = []
    for perm_class in self.permission_classes:
      perm_instances.append(perm_class())
    return perm_instances
  
  def get_shard(self):
    path = self.request.path
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    if first_segment in ['punjab', 'sindh']:
      return first_segment
    return 'default'

  def get_queryset(self):
    queryset = self.queryset.using(self.get_shard()).select_related('parcel').all()
    user_control = self.request.auth.get('control')
    user_uuid = self.request.user_id
    if user_control == 'registrar':
      return queryset
    if user_control == 'tehsildar':
      return queryset
    if user_control == 'citizen':
      return queryset.filter(owner_uuid=user_uuid)
    return queryset.none()
  
  def perform_create(self, serializer):
    parcel = serializer.validated_data['parcel']
    shard = self.get_shard()
    acquisition_type = serializer.validated_data.pop('acquisition_type', 'purchase')
    price = serializer.validated_data.pop('price', 0.00)
   
    has_stay = StayOrder.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
    if has_stay:
      raise serializers.ValidationError('the parcel is locked bcz of active stay order')
    has_charge = Charge.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
    if has_charge:
      raise serializers.ValidationError('the parcel is locked bcz of active bank charge')
    if parcel.status != 'locked':
      raise serializers.ValidationError('the parcel must be locked by the process before the transfer.')
    share = serializer.validated_data.get('share_perc')
    is_valid, msg = TitleValidationService.validate_shares(parcel.id, new_share=float(share), shard=shard)
    if not is_valid:
      raise serializers.ValidationError(msg)
    exis_title = Title.objects.using(shard).filter(parcel=parcel).order_by('-created_at').first()
    if exis_title:
      prev_owner = exis_title.owner_uuid
    else:
      prev_owner = None
    if exis_title:
      exis_title.delete()
    title = serializer.save()
    parcel.status = 'available'
    parcel.save(using=shard)
    ref_code = f'{acquisition_type.upper()} {uuid.uuid4().hex[:8].upper()}'
    
    Ledger.objects.using(shard).create(parcel=parcel, from_owner_uuid=prev_owner, to_owner_uuid=title.owner_uuid,
      transaction_ref=ref_code, price=price)
    
class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = LedgerSerializer
  queryset = Ledger.objects.all()
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
    parcel_id = self.request.query_params.get('parcel_id')
    if parcel_id:
      queryset = queryset.filter(parcel_id=parcel_id)
    if control_role in ['registrar', 'tehsildar']:
      return queryset.order_by('-created_at')
  
    return queryset.filter(Q(from_owner_uuid=user_uuid) | Q(to_owner_uuid=user_uuid)).order_by('-created_at')