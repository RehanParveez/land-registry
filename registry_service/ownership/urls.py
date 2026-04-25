from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ownership.views import TitleViewSet, LedgerViewSet

router = DefaultRouter()
router.register(r'title', TitleViewSet, basename = 'title')
router.register(r'ledger', LedgerViewSet, basename = 'ledger')

urlpatterns = [
  path('', include(router.urls)),   
]