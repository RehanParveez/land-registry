from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import WalletViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'wallet', WalletViewSet, basename = 'wallet')
router.register(r'payment', PaymentViewSet, basename = 'payment')

urlpatterns = [
  path('', include(router.urls)),   
]