from rest_framework.permissions import BasePermission

class CitizenPermission(BasePermission):
  def has_permission(self, request, view):
    if not request.auth:
      return False 
    control_role = request.auth.get('control')  
    if control_role =='citizen':
      request.user_id = request.auth.get('user_id')
      return True
            
    return False

class RegistrarPermission(BasePermission):
  def has_permission(self, request, view):
    print(f'payload: {request.auth}')
    if not request.auth:
      print('no auth pres')
      return False
    control_role = request.auth.get('control')
    if control_role == 'registrar':
      request.user_id = request.auth.get('user_id')
      return True
       
    return False
 
  def has_object_permission(self, request, view, obj):
    return True