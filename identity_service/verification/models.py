from django.db import models
from common.models import BaseModel
from accounts.models import User

class VerificationRec(BaseModel):
  METHOD_CHOICES = (
    ('cnic', 'CNIC'),
    ('biometric', 'Biometric'),
    ('manual', 'Manual')
  )
    
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'verification_recs')
  method = models.CharField(max_length=40, choices=METHOD_CHOICES)
  status = models.CharField(max_length=40, choices=STATUS_CHOICES, default = 'pending')
  metadata = models.JSONField(default=dict, blank=True) 

  def __str__(self):
    return f'{self.user.email}'