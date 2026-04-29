from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from contracts.models import Agreement
from contracts.services import ContractStateMachine
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def unpaid_deals():
  cutoff_time = timezone.now() - timedelta(hours=24)
  old_agreems = Agreement.objects.filter(status = 'draft', created_at__lt=cutoff_time)
    
  cancelled_count = 0
  for agreement in old_agreems:
    ContractStateMachine.transition(agreement, 'cancelled')
    cancelled_count += 1
        
    send_mail(subject = 'the sale agree has exp', message=f'{agreement.id} for parcel {agreement.parcel_id} was cancelled bcz of no paym',
      from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[settings.EMAIL_HOST_USER], fail_silently=False)
    print(f'{agreement.id} cancelled bcz of no paym')
    
  return f'{cancelled_count} agreems cancelled'