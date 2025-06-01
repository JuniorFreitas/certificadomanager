from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    # URLs de Permissões (específicas primeiro)
    path('', views.permission_list, name='list'),
    path('create/', views.permission_create, name='create'),
    path('bulk/', views.bulk_permissions, name='bulk'),
    
    # URLs de Roles (específicas primeiro)
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<str:role_id>/', views.role_detail, name='role_detail'),
    path('roles/<str:role_id>/edit/', views.role_edit, name='role_edit'),
    path('roles/<str:role_id>/delete/', views.role_delete, name='role_delete'),
    
    # URLs de Associações Usuário-Role
    path('user-roles/', views.user_role_list, name='user_role_list'),
    path('user-roles/create/', views.user_role_create, name='user_role_create'),
    path('user-roles/<str:user_role_id>/edit/', views.user_role_edit, name='user_role_edit'),
    path('user-roles/<str:user_role_id>/delete/', views.user_role_delete, name='user_role_delete'),
    
    # URLs AJAX
    path('ajax/user/<str:user_id>/permissions/', views.get_user_permissions, name='get_user_permissions'),
    path('ajax/permission/<str:permission_id>/toggle/', views.toggle_permission, name='toggle_permission'),
    
    # URLs de Permissões (genéricas por último)
    path('<str:permission_id>/', views.permission_detail, name='detail'),
    path('<str:permission_id>/edit/', views.permission_edit, name='edit'),
    path('<str:permission_id>/delete/', views.permission_delete, name='delete'),
] 