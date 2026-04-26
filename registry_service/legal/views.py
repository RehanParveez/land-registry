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
  
  @action(detail=True, methods=['post'])
  def release_stay(self, request, pk=None, shard=None):
    stay = self.get_object()
    stay.is_active = False
    stay.save()
    parcel = stay.parcel  
    other_stays = StayOrder.objects.filter(parcel=parcel, is_active=True).exists()
    active_charges = Charge.objects.filter(parcel=parcel, is_active=True).exists()

    if not other_stays:
      if not active_charges:
        parcel.status = 'available'
        parcel.save()
        return Response({'message': 'the land is now available'}, status=200)

    return Response({'message': 'the stay is rel but land remains locked'}, status=200)

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
  
  @action(detail=True, methods=['post'])
  def release_charge(self, request, pk=None, shard=None):
    charge = self.get_object()
    charge.is_active = False
    charge.save()
    parcel = charge.parcel
    active_stays = StayOrder.objects.filter(parcel=parcel, is_active=True).exists()
    other_charges = Charge.objects.filter(parcel=parcel, is_active=True).exists()

    if not active_stays:
      if not other_charges:
        parcel.status = 'available'
        parcel.save()
        return Response({'message': 'the land is now available'}, status=200)

    return Response({'message': 'the charge is rel but land remains locked'}, status=200)