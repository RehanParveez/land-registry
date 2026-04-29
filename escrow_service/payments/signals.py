from django.dispatch import receiver
from django.db.models.signals import post_save
from contracts.models import Agreement
from payments.models import Wallet, Payment
from payments.tasks import payment_notifi
from contracts.services import ContractStateMachine

@receiver(post_save, sender=Agreement)
def wallet_on_agreement(sender, instance, created, **kwargs):
  if created:
    Wallet.objects.create(agreement=instance)

@receiver(post_save, sender=Payment)
def payment_email(sender, instance, created, **kwargs):
  if created:
    buyer_email = 'rehanrural@gmail.com'
    payment_notifi.delay(email=buyer_email, amount=str(instance.amount), status=instance.status)
    print(f'payment {buyer_email} amount {instance.amount}')
    
@receiver(post_save, sender=Payment)
def on_payment_failure(sender, instance, created, **kwargs):
  if not created:
    return
  if instance.status != 'failed':
    return
  agreement = instance.wallet.agreement
  print(f'failed paym {agreement.id}')
  ContractStateMachine.transition(agreement, 'cancelled')
  print(f'agreement {agreement.id} cancelled')