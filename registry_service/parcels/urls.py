from django.urls import path, include
from rest_framework.routers import DefaultRouter
from parcels.views import ParcelViewSet

router = DefaultRouter()
router.register(r'parcel', ParcelViewSet, basename = 'parcel')

urlpatterns = [
  path('', include(router.urls)),   
]