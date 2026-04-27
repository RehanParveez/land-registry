from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def payment_notifi(email, amount, status):
  subject = 'payment update'
  if status == 'success':
    message = f'payment of {amount} done'
  else:
    message = f'payment of {amount} failed'
  send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False)