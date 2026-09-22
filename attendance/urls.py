from django.urls import path
from . import views
app_name = 'attendance'
urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('mark/', views.mark_attendance, name='mark'),
    path('<int:pk>/delete/', views.attendance_delete, name='delete'),
]
