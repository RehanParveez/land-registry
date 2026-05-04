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
    buyer_id = instance.wallet.agreement.buyer_uuid
    target_email = 'rehanrural@gmail.com'
    form_amount = f'{instance.amount:.2f}'
    payment_notifi.delay(email=target_email, amount=form_amount, status=instance.status)
    print(f'payment {target_email} amount {form_amount}')
    
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