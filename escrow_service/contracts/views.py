from rest_framework import viewsets
from contracts.serializers import AgreementSerializer
from contracts.models import Agreement
from common.permissions import LandPermission
from django.db.models import Q 
from rest_framework.decorators import action

class AgreementViewSet(viewsets.ModelViewSet):
  serializer_class = AgreementSerializer
  queryset = Agreement.objects.all()
  permission_classes = [LandPermission]
    
  def get_queryset(self):
    control_role = self.request.auth.get('control')
    user_uuid = self.request.user_id
    if control_role in ['registrar', 'tehsildar']:
      return self.queryset.all()
    if control_role == 'agent':   
      return self.queryset.all()
    return self.queryset.filter(Q(buyer_uuid=user_uuid) | Q(seller_uuid=user_uuid))

  def perform_create(self, serializer):
    serializer.save(buyer_uuid=self.request.user_id, status = 'draft')

  @action(detail=False, methods=['post'])
  def initiate(self, request):
    return self.create(request)