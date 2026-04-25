from django.urls import path, include
from rest_framework.routers import DefaultRouter
from legal.views import StayOrderViewSet, ChargeViewSet

router = DefaultRouter()
router.register(r'stayorder', StayOrderViewSet, basename = 'stayorder')
router.register(r'charge', ChargeViewSet, basename = 'charge')

urlpatterns = [
    path('', include(router.urls)),
]