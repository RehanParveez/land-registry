from rest_framework import viewsets
from verification.serializers import VerificationRecSerializer
from verification.models import VerificationRec
from common.permissions import CitizenPermission, RegistrarPermission 
from rest_framework.decorators import action
from rest_framework.response import Response
from verification.services import BiometricService
from django.contrib.auth import get_user_model

class VerificationViewSet(viewsets.ModelViewSet):
  serializer_class = VerificationRecSerializer
  queryset = VerificationRec.objects.all()

  def get_permissions(self):
    if self.action == 'verify_biometric':
      return [(CitizenPermission | RegistrarPermission)()]
    if self.action in ['list', 'retrieve']:
      return [CitizenPermission()]
    return [CitizenPermission()]
        
  def get_queryset(self):
    curr_user = self.request.user
    queryset = self.queryset.filter(user=curr_user)
    return queryset
  
  @action(detail=False, methods=['post'])
  def verify_biometric(self, request):
    user_input_hash = request.data.get('hash')
    if not user_input_hash:
      return Response({'err': 'no biomet hash was provided'}, status=400)
    is_match = BiometricService.verify_hash(user_input_hash)
    if is_match == True:
      final_status = 'success'
    else:
      final_status = 'failed'
    
    User = get_user_model()
    real_user = User.objects.filter(id=request.user.id)
    real_user = real_user.first()

    VerificationRec.objects.create(user=real_user, method = 'biometric', status=final_status, metadata={'received_hash': user_input_hash})
    if is_match == True:
      return Response({'message': 'the biometric verific is done'}, status=200)
        
    return Response({'message': 'the biometric match has failed'}, status=401)
