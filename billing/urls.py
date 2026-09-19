from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('',                  views.bill_list,          name='list'),
    path('create/',           views.bill_create,         name='create'),
    path('<int:pk>/',         views.bill_detail,         name='detail'),
    path('<int:pk>/edit/',    views.bill_edit,            name='edit'),
    path('<int:pk>/delete/',  views.bill_delete,          name='delete'),
    path('<int:pk>/excel/',   views.bill_export_excel,    name='export_excel'),
]
