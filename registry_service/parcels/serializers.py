from rest_framework import serializers
from parcels.models import LandParcel
from topology.models import Mauza

class LandParcelSerializer(serializers.ModelSerializer):
  mauza_name = serializers.ReadOnlyField(source = 'mauza.name')
  mauza = serializers.PrimaryKeyRelatedField(queryset=Mauza.objects.none())
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    request = self.context.get('request')
    if request:
      path = request.path
      parts = path.strip('/').split('/')
      first_segment = parts[0] if parts else 'default'
      shard = first_segment if first_segment in ['punjab', 'sindh'] else 'default'
      self.fields['mauza'].queryset = Mauza.objects.using(shard).all()
      
  class Meta:
    model = LandParcel
    fields = ['id', 'mauza', 'mauza_name', 'khasra_number', 'square_footage', 'land_use', 'status', 'created_at', 'updated_at']
    read_only_fields = ['status', 'created_at', 'updated_at']