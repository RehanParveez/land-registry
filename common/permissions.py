from rest_framework.permissions import BasePermission

class CitizenPermission(BasePermission):
  def has_permission(self, request, view):
    if not request.user:
      return False       
    if not request.user.is_authenticated:
      return False    
    if request.user.control == 'citizen':
      return True
            
    return False

class RegistrarPermission(BasePermission):
  def has_permission(self, request, view):
    if not request.user:
      return False
    if not request.user.is_authenticated:
      return False
            
    if request.user.control == 'registrar':
      return True
          
    return False
 
  def has_object_permission(self, request, view, obj):
    return True