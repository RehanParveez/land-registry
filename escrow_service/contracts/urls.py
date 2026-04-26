from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contracts.views import AgreementViewSet

router = DefaultRouter()
router.register(r'agreement', AgreementViewSet, basename = 'agreement')

urlpatterns = [
  path('', include(router.urls)),   
]