from rest_framework import viewsets, mixins
from ownership.serializers import TitleSerializer, LedgerSerializer
from ownership.models import Title, Ledger
from common.permissions import RegistrarPermission, CitizenPermission

class TitleViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
  serializer_class = TitleSerializer
  queryset = Title.objects.all()
  permission_classes = [RegistrarPermission | CitizenPermission]

  def get_queryset(self):
    queryset = self.queryset.select_related('parcel').all()
    user = self.request.user
    user_control = user.token.get('control')
    if user_control == 'registrar':
      return queryset
    if user_control == 'tehsildar':
      return queryset
    if user_control == 'citizen':
      user_uuid = user.token.get('user_id')
      return queryset.filter(owner_uuid=user_uuid)
    return queryset.none()

class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = LedgerSerializer
  queryset = Ledger.objects.all()
  permission_classes = [RegistrarPermission]

  def get_queryset(self):
    parcel_id = self.request.query_params.get('parcel_id')
    if parcel_id:
      return self.queryset.filter(parcel_id=parcel_id).order_by('-created_at')
    return self.queryset