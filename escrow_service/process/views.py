from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from process.services import TransferProcessOperator
from common.permissions import LandPermission

class ProcessViewSet(viewsets.GenericViewSet):
  permission_classes = [LandPermission]
  @action(detail=False, methods=['post'])
  def start_transfer(self, request):
    auth_token = request.headers.get('Authorization')
    print(f'the token received {auth_token}')
    agreement_id = request.data.get('agreement_id')
    shard = request.data.get('shard', 'punjab') 
    auth_token = request.headers.get('Authorization')
    if not agreement_id:
      return Response({'err': 'the agreement_id is needed to initiate the process'}, status=400)
    result = TransferProcessOperator.execute(agreement_id, shard_name=shard, auth_token=auth_token)
    if result.get('success'):
      return Response(result, status=200)
    return Response(result, status=400)
