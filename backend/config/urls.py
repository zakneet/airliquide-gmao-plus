from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from accounts.views import UserViewSet
from dashboard.views import DashboardView
from inventory.views import BrandViewSet, DeviceModelViewSet, DeviceTypeViewSet, DeviceViewSet
from maintenance.views import DossierViewSet, FaultViewSet, PartViewSet, StockMovementViewSet
from reports.views import DossiersCsvView

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('device-types', DeviceTypeViewSet)
router.register('brands', BrandViewSet)
router.register('device-models', DeviceModelViewSet)
router.register('devices', DeviceViewSet, basename='device')
router.register('dossiers', DossierViewSet, basename='dossier')
router.register('faults', FaultViewSet, basename='fault')
router.register('parts', PartViewSet, basename='part')
router.register('stock-movements', StockMovementViewSet, basename='stockmovement')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/reports/dossiers.csv', DossiersCsvView.as_view(), name='report-dossiers'),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
