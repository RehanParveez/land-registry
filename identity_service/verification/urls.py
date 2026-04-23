from django.urls import path, include
from rest_framework.routers import DefaultRouter
from verification.views import VerificationViewSet

router = DefaultRouter()
router.register(r'verify', VerificationViewSet, basename = 'verify')

urlpatterns = [
  path('', include(router.urls)),   
]