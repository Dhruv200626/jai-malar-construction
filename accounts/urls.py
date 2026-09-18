"""
Accounts URL patterns
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.users_list, name='users_list'),
    path('users/add/', views.user_create, name='user_create'),
]
