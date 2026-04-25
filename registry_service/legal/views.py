from rest_framework import viewsets
from legal.serializers import StayOrderSerializer, ChargeSerializer
from legal.models import StayOrder, Charge
from common.permissions import RegistrarPermission
from rest_framework.decorators import action
from rest_framework.response import Response

class StayOrderViewSet(viewsets.ModelViewSet):
  serializer_class = StayOrderSerializer
  queryset = StayOrder.objects.all()
  permission_classes = [RegistrarPermission]

  def get_queryset(self):
    return self.queryset

  @action(detail=False, methods=['post'])
  def apply_stay(self, request):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'the stay order is applied'}, status=201)
    return Response(serializer.errors, status=400)

class ChargeViewSet(viewsets.ModelViewSet):
  serializer_class = ChargeSerializer
  queryset = Charge.objects.all()
  permission_classes = [RegistrarPermission]

  def get_queryset(self):
    return self.queryset

  @action(detail=False, methods=['post'])
  def apply_charge(self, request):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'the charge is registered'}, status=201)
    return Response(serializer.errors, status=400)