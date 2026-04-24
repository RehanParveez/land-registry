from rest_framework import viewsets
from shards.serializers import GlobalParcelMapSerializer
from shards.models import ParcelArea
from common.permissions import RegistrarPermission
from rest_framework.decorators import action
from django.db import connections
from rest_framework.response import Response

class ShardViewSet(viewsets.ModelViewSet):
  serializer_class = GlobalParcelMapSerializer
  queryset = ParcelArea.objects.all()
  permission_classes = [RegistrarPermission]

  def get_queryset(self):
    all_recs = self.queryset
    return all_recs

  @action(detail=False, methods=['get'])
  def status(self, request):
    report = {}
    shards_to_check = ['default', 'punjab', 'sindh']
        
    for name in shards_to_check:
      db_connection = connections[name]
      check = db_connection.ensure_connection()    
      if check == None:
        report[name] = 'Online'
      else:
        report[name] = 'Offline'
                
    return Response(report)