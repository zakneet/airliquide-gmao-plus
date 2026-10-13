from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from accounts.views import UserViewSet
from inventory.views import BrandViewSet, DeviceModelViewSet, DeviceTypeViewSet, DeviceViewSet
from maintenance.views import DossierViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('device-types', DeviceTypeViewSet)
router.register('brands', BrandViewSet)
router.register('device-models', DeviceModelViewSet)
router.register('devices', DeviceViewSet, basename='device')
router.register('dossiers', DossierViewSet, basename='dossier')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
