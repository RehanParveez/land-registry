from rest_framework import viewsets
from payments.serializers import WalletSerializer, PaymentSerializer
from payments.models import Wallet, Payment
from common.permissions import CitizenPermission
from django.db.models import Q
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from payments.services import MockBankingService
from contracts.services import ContractStateMachine
from rest_framework.response import Response
from decimal import Decimal

class WalletViewSet(viewsets.ModelViewSet):
  serializer_class = WalletSerializer
  queryset = Wallet.objects.all()
  permission_classes = [CitizenPermission]
  
  def get_queryset(self):
    user_uuid = self.request.user_id
    is_buyer = Q(agreement__buyer_uuid=user_uuid)
    is_seller = Q(agreement__seller_uuid=user_uuid)
    user_visib_filter = is_buyer | is_seller
    return self.queryset.filter(user_visib_filter)
  
  @action(detail=False, methods=['post'])
  def deposit(self, request):
    agreement_id = request.data.get('agreement_id')
    amount_val = request.data.get('amount')
    wallet = get_object_or_404(Wallet, agreement_id=agreement_id)
    bank_res = MockBankingService.process_external_payment()
   
    Payment.objects.create(wallet=wallet, amount=amount_val, direction = 'in', status=bank_res['status'].lower(), 
      transaction_id=bank_res['bank_ref'])

    if bank_res['status'] == 'success':
      wallet.balance += Decimal(str(amount_val))
      wallet.save()
      if wallet.balance >= wallet.agreement.agreed_price:
        ContractStateMachine.transition(wallet.agreement, 'funded')
      return Response({'message': 'the peposit is recorded'}, status=200)

    return Response({'err': 'the payment has failed'}, status=400)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = PaymentSerializer
  queryset = Payment.objects.all().order_by('-created_at')
  permission_classes = [CitizenPermission]

  def get_queryset(self):
    user_uuid = self.request.user_id
    is_buyer = Q(wallet__agreement__buyer_uuid=user_uuid)
    is_seller = Q(wallet__agreement__seller_uuid=user_uuid)
        
    return self.queryset.filter(is_buyer | is_seller)