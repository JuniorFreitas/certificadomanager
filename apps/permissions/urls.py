from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Permissões
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/', views.permission_list, name='list'),  # Alias para compatibilidade com testes
    path('permissions/create/', views.permission_create, name='permission_create'),
    path('permissions/create/', views.permission_create, name='create'),  # Alias para compatibilidade com testes
    path('permissions/<str:permission_id>/', views.permission_detail, name='permission_detail'),
    path('permissions/<str:permission_id>/', views.permission_detail, name='detail'),  # Alias para compatibilidade com testes
    path('permissions/<str:permission_id>/edit/', views.permission_edit, name='permission_edit'),
    path('permissions/<str:permission_id>/edit/', views.permission_edit, name='edit'),  # Alias para compatibilidade com testes
    path('permissions/<str:permission_id>/delete/', views.permission_delete, name='permission_delete'),
    path('permissions/<str:permission_id>/delete/', views.permission_delete, name='delete'),  # Alias para compatibilidade com testes
    path('permissions/bulk/', views.bulk_permissions, name='bulk_permissions'),
    path('permissions/bulk/', views.bulk_permissions, name='bulk'),  # Alias para compatibilidade com testes
    
    # Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/<str:role_id>/', views.role_detail, name='role_detail'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<str:role_id>/edit/', views.role_edit, name='role_edit'),
    path('roles/<str:role_id>/delete/', views.role_delete, name='role_delete'),
    
    # User Roles
    path('user-roles/', views.user_role_list, name='user_role_list'),
    path('user-roles/create/', views.user_role_create, name='user_role_create'),
    path('user-roles/<str:user_role_id>/edit/', views.user_role_edit, name='user_role_edit'),
    path('user-roles/<str:user_role_id>/delete/', views.user_role_delete, name='user_role_delete'),
    
    # AJAX
    path('ajax/user/<str:user_id>/permissions/', views.user_permissions_ajax, name='user_permissions_ajax'),
    path('ajax/user/<str:user_id>/permissions/', views.user_permissions_ajax, name='get_user_permissions'),  # Alias para compatibilidade com testes
    path('ajax/permission/<str:permission_id>/toggle/', views.toggle_permission_ajax, name='toggle_permission_ajax'),
    path('ajax/permission/<str:permission_id>/toggle/', views.toggle_permission_ajax, name='toggle_permission'),  # Alias para compatibilidade com testes
    
    # Relatórios
    path('reports/', views.permission_report, name='permission_report'),
] 