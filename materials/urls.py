from django.urls import path
from . import views
app_name = 'materials'
urlpatterns = [
    path('', views.material_list, name='list'),
    path('add/', views.material_add, name='add'),
    path('<int:pk>/edit/', views.material_edit, name='edit'),
    path('<int:pk>/delete/', views.material_delete, name='delete'),
    path('inventory/', views.inventory, name='inventory'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
]
