from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views_stats import stats_json
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    # ── Item 6: Stats — MUST come before admin/ catch-all ──
    path('admin/dashboard/', staff_member_required(
        TemplateView.as_view(template_name='admin/dashboard.html')
    ), name='admin-dashboard'),
    path('admin/stats-json/', stats_json, name='admin-stats-json'),

    # ── Django admin ──
    path('admin/', admin.site.urls),

    # ── API ──
    path('api/auth/', include('accounts.urls')),
    path('api/', include('accounts.urls')),
    path('api/navigation/', include('navigation.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)