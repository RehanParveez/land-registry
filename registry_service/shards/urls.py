from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shards.views import ShardViewSet

router = DefaultRouter()
router.register(r'shard', ShardViewSet, basename = 'shard')

urlpatterns = [
  path('', include(router.urls)),   
]