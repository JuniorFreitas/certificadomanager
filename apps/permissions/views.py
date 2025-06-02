from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Permission, Role, UserRole
from .forms import (
    PermissionForm, RoleForm, UserRoleForm, BulkPermissionForm,
    PermissionSearchForm, RolePermissionForm
)
from apps.users.models import User


@login_required
def dashboard(request):
    """Dashboard do sistema de permissões"""
    context = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_roles': Role.objects.filter(is_active=True).count(),
        'total_permissions': Permission.objects.count(),
        'total_user_roles': UserRole.objects.filter(is_active=True).count(),
        'recent_permissions': Permission.objects.select_related('user').order_by('-data_cad')[:5],
        'recent_user_roles': UserRole.objects.select_related('user', 'role').order_by('-data_cad')[:5],
        'permission_stats': get_permission_statistics(),
        'role_stats': get_role_statistics(),
    }
    return render(request, 'permissions/dashboard.html', context)


def get_permission_statistics():
    """Estatísticas de permissões por módulo"""
    stats = {}
    modules = ['users', 'certificates', 'accounts', 'resources', 'permissions']
    
    for module in modules:
        granted = Permission.objects.filter(
            permission_type__startswith=module,
            granted=True
        ).count()
        
        denied = Permission.objects.filter(
            permission_type__startswith=module,
            granted=False
        ).count()
        
        stats[module] = {
            'granted': granted,
            'denied': denied,
            'total': granted + denied
        }
    
    return stats


def get_role_statistics():
    """Estatísticas de roles"""
    return Role.objects.annotate(
        user_count=Count('userrole__user', distinct=True)
    ).values('name', 'user_count')


# ============ VIEWS DE PERMISSÕES ============

@login_required
def permission_list(request):
    """Lista de permissões"""
    permissions = Permission.objects.select_related('user').order_by('user__nome', 'permission_type')
    
    # Formulário de busca
    search_form = PermissionSearchForm(request.GET)
    if search_form.is_valid():
        if search_form.cleaned_data['user']:
            permissions = permissions.filter(user=search_form.cleaned_data['user'])
        
        if search_form.cleaned_data['permission_type']:
            permissions = permissions.filter(permission_type=search_form.cleaned_data['permission_type'])
        
        if search_form.cleaned_data['granted']:
            granted = search_form.cleaned_data['granted'] == 'true'
            permissions = permissions.filter(granted=granted)
    
    # Busca por texto
    search = request.GET.get('search')
    if search:
        permissions = permissions.filter(
            Q(user__nome__icontains=search) |
            Q(user__email__icontains=search) |
            Q(permission_type__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(permissions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'search': search,
        'total_permissions': permissions.count(),
    }
    return render(request, 'permissions/permission_list.html', context)


@login_required
def permission_create(request):
    """Criação de permissão"""
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            permission = form.save(created_by=request.user.email)
            messages.success(request, 'Permissão criada com sucesso!')
            return redirect('permissions:permission_list')
    else:
        form = PermissionForm()
    
    context = {
        'form': form,
        'title': 'Criar Permissão'
    }
    return render(request, 'permissions/permission_form.html', context)


@login_required
def permission_detail(request, permission_id):
    """Detalhes da permissão"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    context = {
        'permission': permission,
        'title': f'Permissão - {permission.get_permission_type_display()}'
    }
    return render(request, 'permissions/permission_detail.html', context)


@login_required
def permission_edit(request, permission_id):
    """Editar permissão"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=permission)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.usu_atu = request.user.email
            permission.data_atu = timezone.now()
            permission.save()
            messages.success(request, 'Permissão atualizada com sucesso!')
            return redirect('permissions:permission_list')
    else:
        form = PermissionForm(instance=permission)
    
    context = {'form': form, 'permission': permission, 'title': 'Editar Permissão'}
    return render(request, 'permissions/permission_form.html', context)


@login_required
def permission_delete(request, permission_id):
    """Excluir permissão"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        permission.delete()
        messages.success(request, 'Permissão excluída com sucesso!')
        return redirect('permissions:permission_list')
    
    context = {'permission': permission}
    return render(request, 'permissions/permission_confirm_delete.html', context)


@login_required
def bulk_permissions(request):
    """Atribuição em massa de permissões"""
    if request.method == 'POST':
        form = BulkPermissionForm(request.POST)
        if form.is_valid():
            permissions = form.save(request.user.email)
            count = len(permissions)
            action = 'concedidas' if form.cleaned_data['granted'] else 'negadas'
            messages.success(request, f'{count} permissões {action} com sucesso!')
            return redirect('permissions:permission_list')
    else:
        form = BulkPermissionForm()
    
    context = {'form': form, 'title': 'Atribuição em Massa de Permissões'}
    return render(request, 'permissions/bulk_permissions.html', context)


# ============ VIEWS DE USER ROLES ============

@login_required
def user_role_list(request):
    """Lista de associações usuário-role"""
    user_roles = UserRole.objects.select_related('user', 'role').order_by('user__nome', 'role__name')
    
    # Busca
    search = request.GET.get('search')
    if search:
        user_roles = user_roles.filter(
            Q(user__nome__icontains=search) |
            Q(user__email__icontains=search) |
            Q(role__name__icontains=search)
        )
    
    # Filtro por status
    status = request.GET.get('status')
    if status == 'active':
        user_roles = user_roles.filter(is_active=True)
    elif status == 'inactive':
        user_roles = user_roles.filter(is_active=False)
    
    # Paginação
    paginator = Paginator(user_roles, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'total_user_roles': user_roles.count(),
    }
    return render(request, 'permissions/user_role_list.html', context)


@login_required
def user_role_create(request):
    """Criar nova associação usuário-role"""
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            user_role = form.save(commit=False)
            user_role.usu_cad = request.user.email
            user_role.save()
            messages.success(request, f'Role "{user_role.role.get_name_display()}" atribuído ao usuário "{user_role.user.nome}" com sucesso!')
            return redirect('permissions:user_role_list')
    else:
        form = UserRoleForm()
    
    context = {'form': form, 'title': 'Atribuir Role a Usuário'}
    return render(request, 'permissions/user_role_form.html', context)


@login_required
def user_role_edit(request, user_role_id):
    """Editar associação usuário-role"""
    user_role = get_object_or_404(UserRole, id=user_role_id)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user_role)
        if form.is_valid():
            user_role = form.save(commit=False)
            user_role.usu_atu = request.user.email
            user_role.data_atu = timezone.now()
            user_role.save()
            messages.success(request, 'Associação usuário-role atualizada com sucesso!')
            return redirect('permissions:user_role_list')
    else:
        form = UserRoleForm(instance=user_role)
    
    context = {'form': form, 'user_role': user_role, 'title': 'Editar Associação Usuário-Role'}
    return render(request, 'permissions/user_role_form.html', context)


@login_required
def user_role_delete(request, user_role_id):
    """Excluir associação usuário-role"""
    user_role = get_object_or_404(UserRole, id=user_role_id)
    
    if request.method == 'POST':
        user_role.delete()
        messages.success(request, 'Associação usuário-role excluída com sucesso!')
        return redirect('permissions:user_role_list')
    
    context = {'user_role': user_role}
    return render(request, 'permissions/user_role_confirm_delete.html', context)


# ============ VIEWS AJAX ============

@login_required
@require_http_methods(["GET"])
def user_permissions_ajax(request, user_id):
    """Retorna as permissões de um usuário via AJAX"""
    user = get_object_or_404(User, id=user_id)
    permissions = Permission.objects.filter(user=user).values(
        'permission_type', 'granted'
    )
    
    # Formatando as permissões para o formato esperado
    permissions_list = []
    for perm in permissions:
        permissions_list.append({
            'type': perm['permission_type'],
            'granted': perm['granted']
        })
    
    return JsonResponse({
        'success': True,
        'user': user.nome,
        'permissions': permissions_list
    })


@login_required
@require_http_methods(["POST"])
def toggle_permission_ajax(request, permission_id):
    """Alterna o status de uma permissão via AJAX"""
    permission = get_object_or_404(Permission, id=permission_id)
    permission.granted = not permission.granted
    permission.usu_atu = request.user.email
    permission.data_atu = timezone.now()
    permission.save()
    
    return JsonResponse({
        'success': True,
        'granted': permission.granted,
        'message': f'Permissão {"concedida" if permission.granted else "negada"} com sucesso!'
    })


# ============ VIEWS DE RELATÓRIOS ============

@login_required
def permission_report(request):
    """Relatório de permissões"""
    # Estatísticas gerais
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_permissions': Permission.objects.count(),
        'granted_permissions': Permission.objects.filter(granted=True).count(),
        'denied_permissions': Permission.objects.filter(granted=False).count(),
    }
    
    # Permissões por módulo
    module_stats = get_permission_statistics()
    
    # Usuários com mais permissões
    top_users = User.objects.annotate(
        permission_count=Count('permission')
    ).filter(permission_count__gt=0).order_by('-permission_count')[:10]
    
    # Permissões mais comuns
    common_permissions = Permission.objects.values('permission_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'stats': stats,
        'module_stats': module_stats,
        'top_users': top_users,
        'common_permissions': common_permissions,
    }
    return render(request, 'permissions/permission_report.html', context)


# ============ VIEWS DE ROLES ============

@login_required
def role_list(request):
    """Lista de roles"""
    roles = Role.objects.all().order_by('name')
    
    # Busca
    search = request.GET.get('search')
    if search:
        roles = roles.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Filtro por status
    status = request.GET.get('status')
    if status == 'active':
        roles = roles.filter(is_active=True)
    elif status == 'inactive':
        roles = roles.filter(is_active=False)
    
    # Paginação
    paginator = Paginator(roles, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'total_roles': roles.count(),
    }
    return render(request, 'permissions/role_list.html', context)


@login_required
def role_detail(request, role_id):
    """Detalhes do role"""
    role = get_object_or_404(Role, id=role_id)
    
    # Usuários com este role
    user_roles = UserRole.objects.filter(role=role, is_active=True).select_related('user')
    
    context = {
        'role': role,
        'user_roles': user_roles,
        'total_users': user_roles.count(),
    }
    return render(request, 'permissions/role_detail.html', context)


@login_required
def role_create(request):
    """Criar novo role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.usu_cad = request.user.email
            role.save()
            messages.success(request, f'Role "{role.get_name_display()}" criado com sucesso!')
            return redirect('permissions:role_list')
    else:
        form = RoleForm()
    
    context = {'form': form, 'title': 'Criar Role'}
    return render(request, 'permissions/role_form.html', context)


@login_required
def role_edit(request, role_id):
    """Editar role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            role.usu_atu = request.user.email
            role.data_atu = timezone.now()
            role.save()
            messages.success(request, f'Role "{role.get_name_display()}" atualizado com sucesso!')
            return redirect('permissions:role_list')
    else:
        form = RoleForm(instance=role)
    
    context = {'form': form, 'role': role, 'title': 'Editar Role'}
    return render(request, 'permissions/role_form.html', context)


@login_required
def role_delete(request, role_id):
    """Excluir role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role_name = role.get_name_display()
        role.delete()
        messages.success(request, f'Role "{role_name}" excluído com sucesso!')
        return redirect('permissions:role_list')
    
    context = {'role': role}
    return render(request, 'permissions/role_confirm_delete.html', context)
