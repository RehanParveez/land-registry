from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user_sessions.views import SessionViewSet

router = DefaultRouter()
router.register(r'session', SessionViewSet, basename = 'session')

urlpatterns = [
  path('', include(router.urls)),   
]