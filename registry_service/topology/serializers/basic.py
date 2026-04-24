from rest_framework import serializers
from topology.models import Tehsil, Mauza

class TehsilSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Tehsil
    fields = ['id', 'name']
        
class MauzaSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Mauza
    fields = ['id', 'name']