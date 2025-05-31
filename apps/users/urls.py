from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('create/', views.user_create, name='create'),
    path('<str:user_id>/', views.user_detail, name='detail'),
    path('<str:user_id>/edit/', views.user_edit, name='edit'),
    path('<str:user_id>/delete/', views.user_delete, name='delete'),
] 