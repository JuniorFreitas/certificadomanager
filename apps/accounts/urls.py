from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # URLs principais
    path('', views.account_list, name='list'),
    path('create/', views.account_create, name='create'),
    path('<str:account_id>/', views.account_detail, name='detail'),
    path('<str:account_id>/edit/', views.account_edit, name='edit'),
    path('<str:account_id>/delete/', views.account_delete, name='delete'),
    
    # URLs para testes e validação
    path('<str:account_id>/test/', views.account_test, name='test'),
    path('<str:account_id>/validate/', views.account_validate, name='validate'),
    path('<str:account_id>/resources/', views.account_resources, name='resources'),
    
    # URLs para ações em lote
    path('bulk/actions/', views.bulk_actions, name='bulk_actions'),
    
    # APIs AJAX
    path('api/<str:account_id>/status/', views.api_account_status, name='api_status'),
    path('api/<str:account_id>/validate/', views.api_quick_validate, name='api_validate'),
    path('api/<str:account_id>/resources/', views.api_account_resources, name='api_resources'),
    
    # URLs para gerenciar regiões
    path('<str:account_id>/regions/create/', views.region_create, name='region_create'),
    path('<str:account_id>/regions/<str:region_id>/delete/', views.region_delete, name='region_delete'),
] 