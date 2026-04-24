from django.db import models
from common.models import BaseModel

SHARD_CHOICES = (
  ('punjab', 'Punjab'),
  ('sindh', 'Sindh'),
)

class Topology(BaseModel):
  name = models.CharField(max_length=255)
  code = models.CharField(max_length=50, unique=True)

  class Meta:
    abstract = True
    ordering = ['name']
        
  def __str__(self):
    return f'{self.name}'

class Province(Topology):
  database_alias = models.CharField(max_length=50, choices=SHARD_CHOICES, default = 'punjab',
    help_text = 'the inter id of the database shard for this prov')

class Division(Topology):
  province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name = 'divisions')

class District(Topology):
  division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name = 'districts')

class Tehsil(Topology):
  district = models.ForeignKey(District, on_delete=models.CASCADE, related_name = 'tehsils')

class Mauza(Topology):
  tehsil = models.ForeignKey(Tehsil, on_delete=models.CASCADE, related_name = 'mauzas')
  
  def __str__(self):
    return f'{self.name} ({self.tehsil.name})'