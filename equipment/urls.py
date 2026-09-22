from django.urls import path
from . import views
app_name = 'equipment'
urlpatterns = [
    path('', views.equipment_list, name='list'),
    path('add/', views.equipment_add, name='add'),
    path('<int:pk>/edit/', views.equipment_edit, name='edit'),
    path('<int:pk>/delete/', views.equipment_delete, name='delete'),
]
