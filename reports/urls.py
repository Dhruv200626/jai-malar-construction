from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('daily/', views.daily_reports, name='daily'),
    path('daily/add/', views.daily_report_add, name='daily_add'),
    path('monthly/', views.monthly_reports, name='monthly'),
    path('analytics/', views.analytics, name='analytics'),
]
