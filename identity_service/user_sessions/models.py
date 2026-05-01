from django.db import models
from common.models import BaseModel
from accounts.models import User

class ActiveSession(BaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'active_sessions')
  session_key = models.CharField(max_length=300, unique=True)
  ip_address = models.GenericIPAddressField()
  user_agent = models.TextField()
  is_flagged = models.BooleanField(default=False)

  def __str__(self):
    return f'{self.user.email}'