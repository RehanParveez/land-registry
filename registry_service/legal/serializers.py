from rest_framework import serializers
from legal.models import StayOrder, Charge
from parcels.models import LandParcel

class StayOrderSerializer(serializers.ModelSerializer):
  parcel = serializers.PrimaryKeyRelatedField(queryset=LandParcel.objects.none())
  class Meta:
    model = StayOrder
    fields = ['id', 'parcel', 'description', 'court_name', 'case_num', 'issue_date', 'expiry_date', 'is_active', 'created_at', 'updated_at']
    read_only_fields = ['created_at', 'updated_at']
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    request = self.context.get('request')
    if request:
      path = request.path
      parts = path.strip('/').split('/')
      first_segment = parts[0] if parts else 'default'
      shard = first_segment if first_segment in ['punjab', 'sindh'] else 'default'
      self.fields['parcel'].queryset = LandParcel.objects.using(shard).all()
  
  def create(self, validated_data):
    request = self.context.get('request')
    path = request.path if request else ''
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    shard = first_segment if first_segment in ['punjab', 'sindh'] else 'default'
    stay = super().create(validated_data)
    parcel = stay.parcel
    parcel.status = 'locked'
    parcel.save(using=shard)
    return stay

class ChargeSerializer(serializers.ModelSerializer):
  parcel = serializers.PrimaryKeyRelatedField(queryset=LandParcel.objects.none())
  class Meta:
    model = Charge
    fields = ['id', 'parcel', 'bank_name', 'loan_acc_num', 'loan_amount', 'currency', 'registration_date', 'is_active', 'created_at', 'updated_at']
    read_only_fields = ['registration_date', 'created_at', 'updated_at']
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    request = self.context.get('request')
    if request:
      path = request.path
      parts = path.strip('/').split('/')
      first_segment = parts[0] if parts else 'default'
      shard = first_segment if first_segment in ['punjab', 'sindh'] else 'default'
      self.fields['parcel'].queryset = LandParcel.objects.using(shard).all()

  def create(self, validated_data):
    request = self.context.get('request')
    path = request.path if request else ''
    parts = path.strip('/').split('/')
    first_segment = parts[0] if parts else 'default'
    shard = first_segment if first_segment in ['punjab', 'sindh'] else 'default'
    charge = super().create(validated_data)
    parcel = charge.parcel
    parcel.status = 'locked'
    parcel.save(using=shard)
    return charge