from rest_framework import viewsets, mixins, serializers
from ownership.serializers import TitleSerializer, LedgerSerializer
from ownership.models import Title, Ledger
from common.permissions import RegistrarPermission, CitizenPermission
from legal.models import StayOrder, Charge
import uuid

class TitleViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
  serializer_class = TitleSerializer
  queryset = Title.objects.all()
  permission_classes = [RegistrarPermission | CitizenPermission]

  def get_queryset(self):
    queryset = self.queryset.select_related('parcel').all()
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
    shard = self.request.resolver_match.kwargs.get('shard')
    acquisition_type = serializer.validated_data.pop('acquisition_type', 'purchase')
    price = serializer.validated_data.pop('price', 0.00)
   
    has_stay = StayOrder.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
    if has_stay:
      raise serializers.ValidationError('the parcel is locked bcz of active stay order')
    has_charge = Charge.objects.using(shard).filter(parcel=parcel, is_active=True).exists()
    if has_charge:
      raise serializers.ValidationError('the parcel is locked bcz of active bank charge')
    if parcel.status == 'locked':
      raise serializers.ValidationError('the parcel must be locked by the process before the transfer.')
    
    last_entry = Ledger.objects.using(shard).filter(parcel=parcel).order_by('-created_at').first()
    prev_owner = None
    if last_entry:
        prev_owner = last_entry.to_owner_uuid
    title = serializer.save()
    parcel.status = 'available'
    parcel.save(using=shard)
    ref_code = f'{acquisition_type.upper()} {uuid.uuid4().hex[:8].upper()}'
    
    Ledger.objects.using(shard).create(parcel=parcel, from_owner_uuid=prev_owner, to_owner_uuid=title.owner_uuid,
      transaction_ref=ref_code, price=price)
    
class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = LedgerSerializer
  queryset = Ledger.objects.all()
  permission_classes = [RegistrarPermission]

  def get_queryset(self):
    parcel_id = self.request.query_params.get('parcel_id')
    if parcel_id:
      return self.queryset.filter(parcel_id=parcel_id).order_by('-created_at')
    return self.queryset