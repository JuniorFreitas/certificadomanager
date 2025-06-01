from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from .models import Permission, Role, UserRole
from .forms import (
    PermissionForm, RoleForm, UserRoleForm, 
    PermissionSearchForm, BulkPermissionForm
)
from apps.users.models import User


# ============ VIEWS DE PERMISSÕES ============

@login_required
def permission_list(request):
    """Lista todas as permissões com busca avançada e paginação"""
    form = PermissionSearchForm(request.GET)
    permissions = Permission.objects.select_related('user').order_by('-data_cad')
    
    # Aplicar filtros de busca
    if form.is_valid():
        search = form.cleaned_data.get('search')
        permission_type = form.cleaned_data.get('permission_type')
        granted = form.cleaned_data.get('granted')
        user = form.cleaned_data.get('user')
        
        if search:
            permissions = permissions.filter(
                Q(user__nome__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        if permission_type:
            permissions = permissions.filter(permission_type=permission_type)
            
        if granted:
            permissions = permissions.filter(granted=granted == 'true')
        
        if user:
            permissions = permissions.filter(user=user)
    
    # Paginação
    paginator = Paginator(permissions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': Permission.objects.count(),
        'granted': Permission.objects.filter(granted=True).count(),
        'revoked': Permission.objects.filter(granted=False).count(),
        'users_with_permissions': Permission.objects.values('user').distinct().count(),
    }
    
    return render(request, 'permissions/list.html', {
        'page_obj': page_obj,
        'form': form,
        'stats': stats
    })


@login_required
def permission_detail(request, permission_id):
    """Exibe detalhes de uma permissão específica"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    # Outras permissões do mesmo usuário
    user_permissions = Permission.objects.filter(
        user=permission.user
    ).exclude(id=permission.id).order_by('permission_type')
    
    return render(request, 'permissions/detail.html', {
        'permission': permission,
        'user_permissions': user_permissions
    })


@login_required
def permission_create(request):
    """Cria uma nova permissão"""
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.usu_cad = request.user.email
            permission.save()
            messages.success(request, 'Permissão criada com sucesso!')
            return redirect('permissions:detail', permission_id=permission.id)
    else:
        form = PermissionForm()
    
    return render(request, 'permissions/form.html', {
        'form': form,
        'title': 'Criar Permissão'
    })


@login_required
def permission_edit(request, permission_id):
    """Edita uma permissão existente"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=permission)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.usu_atu = request.user.email
            permission.data_atu = timezone.now()
            permission.save()
            messages.success(request, 'Permissão atualizada com sucesso!')
            return redirect('permissions:detail', permission_id=permission.id)
    else:
        form = PermissionForm(instance=permission)
    
    return render(request, 'permissions/form.html', {
        'form': form,
        'title': 'Editar Permissão',
        'permission': permission
    })


@login_required
def permission_delete(request, permission_id):
    """Exclui uma permissão"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        user_name = permission.user.nome
        permission_name = permission.get_permission_type_display()
        permission.delete()
        messages.success(request, f'Permissão "{permission_name}" do usuário "{user_name}" excluída com sucesso!')
        return redirect('permissions:list')
    
    return render(request, 'permissions/delete.html', {
        'permission': permission
    })


@login_required
def bulk_permissions(request):
    """Concessão em lote de permissões"""
    if request.method == 'POST':
        form = BulkPermissionForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data['users']
            permissions = form.cleaned_data['permissions']
            granted = form.cleaned_data['granted']
            
            created_count = 0
            updated_count = 0
            
            with transaction.atomic():
                for user in users:
                    for permission_type in permissions:
                        permission, created = Permission.objects.get_or_create(
                            user=user,
                            permission_type=permission_type,
                            defaults={
                                'granted': granted,
                                'usu_cad': request.user.email
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            permission.granted = granted
                            permission.usu_atu = request.user.email
                            permission.data_atu = timezone.now()
                            permission.save()
                            updated_count += 1
            
            action = 'concedidas' if granted else 'revogadas'
            messages.success(
                request, 
                f'Permissões {action} com sucesso! '
                f'{created_count} criadas, {updated_count} atualizadas.'
            )
            return redirect('permissions:list')
    else:
        form = BulkPermissionForm()
    
    return render(request, 'permissions/bulk_form.html', {
        'form': form,
        'title': 'Concessão em Lote'
    })


# ============ VIEWS DE ROLES ============

@login_required
def role_list(request):
    """Lista todos os roles"""
    roles = Role.objects.annotate(
        user_count=Count('userrole')
    ).order_by('name')
    
    # Estatísticas
    stats = {
        'total': Role.objects.count(),
        'active': Role.objects.filter(is_active=True).count(),
        'inactive': Role.objects.filter(is_active=False).count(),
    }
    
    return render(request, 'permissions/role_list.html', {
        'roles': roles,
        'stats': stats
    })


@login_required
def role_detail(request, role_id):
    """Exibe detalhes de um role específico"""
    role = get_object_or_404(Role, id=role_id)
    
    # Usuários com este role
    user_roles = UserRole.objects.filter(role=role).select_related('user')
    
    return render(request, 'permissions/role_detail.html', {
        'role': role,
        'user_roles': user_roles
    })


@login_required
def role_create(request):
    """Cria um novo role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.usu_cad = request.user.email
            role.save()
            messages.success(request, 'Role criado com sucesso!')
            return redirect('permissions:role_detail', role_id=role.id)
    else:
        form = RoleForm()
    
    return render(request, 'permissions/role_form.html', {
        'form': form,
        'title': 'Criar Role'
    })


@login_required
def role_edit(request, role_id):
    """Edita um role existente"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            role.usu_atu = request.user.email
            role.data_atu = timezone.now()
            role.save()
            messages.success(request, 'Role atualizado com sucesso!')
            return redirect('permissions:role_detail', role_id=role.id)
    else:
        form = RoleForm(instance=role)
    
    return render(request, 'permissions/role_form.html', {
        'form': form,
        'title': 'Editar Role',
        'role': role
    })


@login_required
def role_delete(request, role_id):
    """Exclui um role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role_name = role.get_name_display()
        role.delete()
        messages.success(request, f'Role "{role_name}" excluído com sucesso!')
        return redirect('permissions:role_list')
    
    return render(request, 'permissions/role_delete.html', {
        'role': role
    })


# ============ VIEWS DE ASSOCIAÇÕES USUÁRIO-ROLE ============

@login_required
def user_role_list(request):
    """Lista todas as associações usuário-role"""
    user_roles = UserRole.objects.select_related('user', 'role').order_by('user__nome', 'role__name')
    
    # Paginação
    paginator = Paginator(user_roles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': UserRole.objects.count(),
        'active': UserRole.objects.filter(is_active=True).count(),
        'inactive': UserRole.objects.filter(is_active=False).count(),
    }
    
    return render(request, 'permissions/user_role_list.html', {
        'page_obj': page_obj,
        'stats': stats
    })


@login_required
def user_role_create(request):
    """Cria uma nova associação usuário-role"""
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            user_role = form.save(commit=False)
            user_role.usu_cad = request.user.email
            user_role.save()
            messages.success(request, 'Associação usuário-role criada com sucesso!')
            return redirect('permissions:user_role_list')
    else:
        form = UserRoleForm()
    
    return render(request, 'permissions/user_role_form.html', {
        'form': form,
        'title': 'Associar Usuário a Role'
    })


@login_required
def user_role_edit(request, user_role_id):
    """Edita uma associação usuário-role"""
    user_role = get_object_or_404(UserRole, id=user_role_id)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user_role)
        if form.is_valid():
            user_role = form.save(commit=False)
            user_role.usu_atu = request.user.email
            user_role.data_atu = timezone.now()
            user_role.save()
            messages.success(request, 'Associação atualizada com sucesso!')
            return redirect('permissions:user_role_list')
    else:
        form = UserRoleForm(instance=user_role)
    
    return render(request, 'permissions/user_role_form.html', {
        'form': form,
        'title': 'Editar Associação',
        'user_role': user_role
    })


@login_required
def user_role_delete(request, user_role_id):
    """Exclui uma associação usuário-role"""
    user_role = get_object_or_404(UserRole, id=user_role_id)
    
    if request.method == 'POST':
        user_name = user_role.user.nome
        role_name = user_role.role.get_name_display()
        user_role.delete()
        messages.success(request, f'Associação "{user_name} - {role_name}" excluída com sucesso!')
        return redirect('permissions:user_role_list')
    
    return render(request, 'permissions/user_role_delete.html', {
        'user_role': user_role
    })


# ============ VIEWS AJAX ============

@login_required
def get_user_permissions(request, user_id):
    """Retorna as permissões de um usuário via AJAX"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        user = get_object_or_404(User, id=user_id)
        permissions = Permission.objects.filter(user=user).order_by('permission_type')
        
        permission_data = []
        for perm in permissions:
            permission_data.append({
                'id': perm.id,
                'type': perm.permission_type,
                'type_display': perm.get_permission_type_display(),
                'granted': perm.granted,
                'module': perm.module_name,
                'action': perm.action_name,
            })
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.nome,
                'email': user.email
            },
            'permissions': permission_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def toggle_permission(request, permission_id):
    """Alterna o status de uma permissão via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        permission = get_object_or_404(Permission, id=permission_id)
        permission.granted = not permission.granted
        permission.usu_atu = request.user.email
        permission.data_atu = timezone.now()
        permission.save()
        
        action = 'concedida' if permission.granted else 'revogada'
        
        return JsonResponse({
            'success': True,
            'granted': permission.granted,
            'message': f'Permissão {action} com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
