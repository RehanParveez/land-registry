from rest_framework.permissions import BasePermission
from django.apps import apps

class LandPermission(BasePermission):
  def has_permission(self, request, view):
    if not request.auth:
      return False 
    role = request.auth.get('control')
    request.user_id = request.auth.get('user_id')
    if role == 'registrar':
      return True
    return role in ['citizen', 'tehsildar', 'agent']
  
  def has_object_permission(self, request, view, obj):
    role = request.auth.get('control')
    if role == 'registrar':
      return True  
    user_id = str(request.user_id)
        
    if hasattr(obj, 'owner_uuid'):
      return str(obj.owner_uuid) == user_id
            
    if hasattr(obj, 'buyer_uuid') or hasattr(obj, 'seller_uuid'):
      is_buyer = str(getattr(obj, 'buyer_uuid', '')) == user_id
      is_seller = str(getattr(obj, 'seller_uuid', '')) == user_id
      return is_buyer or is_seller
    
    if hasattr(obj, 'from_owner_uuid') or hasattr(obj, 'to_owner_uuid'):
      is_from = str(getattr(obj, 'from_owner_uuid', '')) == user_id
      is_to = str(getattr(obj, 'to_owner_uuid', '')) == user_id
      return is_from or is_to

    if hasattr(obj, 'user'):
      obj_user_id = getattr(obj.user, 'id', obj.user)
      return str(obj_user_id) == user_id
    if hasattr(obj, 'email') and hasattr(obj, 'id'):
        return str(obj.id) == user_id
      
    return False
  
class IdentityPermission(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if not hasattr(request.user, 'profile'):
      return False
    profile = request.user.profile
    if not profile.is_verified:
      return False
    return True

class RegistrarPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
      return True
    if not request.auth:
      return False
    role = request.auth.get('control')
    return role == 'registrar'

class EnoughEscrowPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method != 'POST':
      return True
    agreement_id = request.data.get('agreement_id')
    if not agreement_id:
      return False
    wallet = apps.get_model('payments', 'Wallet').objects.filter(agreement_id=agreement_id)
    wallet = wallet.first()
    if not wallet:
      return False
    return wallet.balance >= wallet.agreement.agreed_price