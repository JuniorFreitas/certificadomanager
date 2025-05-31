from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    path('', views.permission_list, name='list'),
    path('create/', views.permission_create, name='create'),
] 