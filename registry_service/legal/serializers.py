from rest_framework import serializers
from legal.models import StayOrder, Charge

class StayOrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = StayOrder
    fields = ['id', 'parcel', 'description', 'court_name', 'case_num', 'issue_date', 'expiry_date', 'is_active', 'created_at', 'updated_at']
    read_only_fields = ['created_at', 'updated_at']
  
  def create(self, validated_data):
    stay = super().create(validated_data)
    parcel = stay.parcel
    parcel.status = 'locked'
    parcel.save()
    return stay

class ChargeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Charge
    fields = ['id', 'parcel', 'bank_name', 'loan_acc_num', 'loan_amount', 'currency', 'registration_date', 'is_active', 'created_at', 'updated_at']
    read_only_fields = ['registration_date', 'created_at', 'updated_at']

  def create(self, validated_data):
    charge = super().create(validated_data)
    parcel = charge.parcel
    parcel.status = 'locked'
    parcel.save()
    return charge