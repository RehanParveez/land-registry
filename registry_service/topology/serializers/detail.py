from rest_framework import serializers
from topology.models import Division, District, Tehsil, Mauza, Province
from topology.serializers.basic import TehsilSerializer1, MauzaSerializer1

class DivisionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Division
    fields = ['name', 'code', 'province']

class DistrictSerializer(serializers.ModelSerializer):
  tehsils = TehsilSerializer1(many=True, read_only=True)
  class Meta:
    model = District
    fields = ['name', 'code', 'tehsils']
           
class TehsilSerializer(serializers.ModelSerializer):
  mauzas = MauzaSerializer1(many=True, read_only=True)
  class Meta:
    model = Tehsil
    fields = ['name', 'code', 'mauzas']

class MauzaSerializer(serializers.ModelSerializer):
  class Meta:
    model = Mauza
    fields = ['name', 'code']

class ProvinceTreeSerializer(serializers.ModelSerializer):
  divisions = serializers.SerializerMethodField()
  class Meta:
    model = Province
    fields = ['name', 'code', 'database_alias', 'divisions']

  def get_divisions(self, obj):
    divisions_qs = obj.divisions.all()
    data = []
    for div in divisions_qs:
      div_data = {'name': div.name, 'districts': DistrictSerializer(div.districts.all(), many=True).data}
      data.append(div_data)
    return data