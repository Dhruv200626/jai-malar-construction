"""
Jai Malhar - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('', include('accounts.urls')),

    # Main modules
    path('dashboard/', include('dashboard.urls')),
    path('projects/', include('projects.urls')),
    path('employees/', include('employees.urls')),
    path('attendance/', include('attendance.urls')),
    path('materials/', include('materials.urls')),
    path('expenses/', include('expenses.urls')),
    path('equipment/', include('equipment.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('clients/', include('clients.urls')),
    path('reports/', include('reports.urls')),

    # REST API
    path('api/', include('accounts.api_urls')),
]

# Error handlers
handler400 = 'accounts.views.error_400'
handler403 = 'accounts.views.error_403'
handler404 = 'accounts.views.error_404'
handler500 = 'accounts.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
