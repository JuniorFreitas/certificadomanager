from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resource_list, name='list'),
    path('create/', views.resource_create, name='create'),
    path('<str:resource_id>/', views.resource_detail, name='detail'),
    path('<str:resource_id>/edit/', views.resource_edit, name='edit'),
    path('<str:resource_id>/delete/', views.resource_delete, name='delete'),
    path('<str:resource_id>/test-connection/', views.test_resource_connection, name='test_connection'),
] 