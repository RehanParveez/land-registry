from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import AuthenticationViewSet, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'identity', AuthenticationViewSet, basename = 'identity')

urlpatterns = [
    path('', include(router.urls)),
    path('tokenobtainpair/', CustomTokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('tokenrefresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
]