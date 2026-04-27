from django.urls import path, include
from rest_framework.routers import DefaultRouter
from process.views import ProcessViewSet

router = DefaultRouter()
router.register(r'transfer', ProcessViewSet, basename = 'transfer')

urlpatterns = [
    path('', include(router.urls)),
]