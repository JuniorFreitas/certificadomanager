#!/usr/bin/env python
"""
Script para criar dados de demonstração para o módulo de permissões
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fcm.settings')
django.setup()

from apps.users.models import User
from apps.permissions.models import Role, Permission, UserRole

def create_permissions_data():
    """Criar dados de demonstração para permissões"""
    
    print("🔐 Criando dados de demonstração para Permissões...")
    
    # 1. Criar Roles
    print("\n📋 Criando Roles...")
    
    roles_data = [
        {
            'name': 'admin',
            'description': 'Administrador do sistema com acesso total',
            'is_active': True
        },
        {
            'name': 'manager',
            'description': 'Gerente com acesso a relatórios e supervisão',
            'is_active': True
        },
        {
            'name': 'user',
            'description': 'Usuário padrão com acesso operacional',
            'is_active': True
        },
        {
            'name': 'viewer',
            'description': 'Visualizador com acesso somente leitura',
            'is_active': True
        }
    ]
    
    roles = {}
    admin_user = User.objects.filter(is_superuser=True).first()
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                **role_data,
                'usu_cad': admin_user.email if admin_user else 'system',
                'usu_atu': admin_user.email if admin_user else 'system'
            }
        )
        roles[role.name] = role
        status = "✅ Criado" if created else "ℹ️  Já existe"
        print(f"   {status}: {role.get_name_display()}")
    
    # 2. Associar usuários a roles
    print("\n👥 Criando associações Usuário-Role...")
    
    # Buscar usuários existentes
    users = User.objects.filter(is_active=True)[:4]  # Pegar até 4 usuários
    
    if users.exists():
        user_role_assignments = [
            (users[0], 'admin'),  # Primeiro usuário como admin
        ]
        
        # Se temos mais usuários, distribuir roles
        if len(users) > 1:
            user_role_assignments.append((users[1], 'manager'))
        if len(users) > 2:
            user_role_assignments.append((users[2], 'user'))
        if len(users) > 3:
            user_role_assignments.append((users[3], 'viewer'))
        
        for user, role_name in user_role_assignments:
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=roles[role_name],
                defaults={
                    'is_active': True,
                    'usu_cad': admin_user.email if admin_user else 'system',
                    'usu_atu': admin_user.email if admin_user else 'system'
                }
            )
            status = "✅ Criada" if created else "ℹ️  Já existe"
            print(f"   {status}: {user.nome} -> {roles[role_name].get_name_display()}")
    else:
        print("   ⚠️  Nenhum usuário encontrado para associar roles")
    
    # 3. Atribuir permissões específicas a alguns usuários
    print("\n🎯 Atribuindo permissões específicas...")
    
    if users.exists():
        # Admin user - todas as permissões
        admin_user_obj = users[0]
        admin_permissions = [
            'users_view', 'users_create', 'users_edit', 'users_delete',
            'certificates_view', 'certificates_create', 'certificates_edit', 'certificates_delete',
            'accounts_view', 'accounts_create', 'accounts_edit', 'accounts_delete',
            'resources_view', 'resources_create', 'resources_edit', 'resources_delete',
            'permissions_view', 'permissions_create', 'permissions_edit', 'permissions_delete'
        ]
        
        for perm_type in admin_permissions:
            permission, created = Permission.objects.get_or_create(
                user=admin_user_obj,
                permission_type=perm_type,
                defaults={
                    'granted': True,
                    'usu_cad': admin_user.email if admin_user else 'system',
                    'usu_atu': admin_user.email if admin_user else 'system'
                }
            )
            if created:
                print(f"   ✅ {admin_user_obj.nome}: {perm_type}")
        
        # Manager user - permissões de visualização e relatórios
        if len(users) > 1:
            manager_user = users[1]
            manager_permissions = [
                'users_view', 'certificates_view',
                'accounts_view', 'resources_view', 'permissions_view'
            ]
            
            for perm_type in manager_permissions:
                permission, created = Permission.objects.get_or_create(
                    user=manager_user,
                    permission_type=perm_type,
                    defaults={
                        'granted': True,
                        'usu_cad': admin_user.email if admin_user else 'system',
                        'usu_atu': admin_user.email if admin_user else 'system'
                    }
                )
                if created:
                    print(f"   ✅ {manager_user.nome}: {perm_type}")
        
        # User - permissões operacionais
        if len(users) > 2:
            regular_user = users[2]
            user_permissions = [
                'certificates_view', 'certificates_create', 'certificates_edit',
                'accounts_view', 'resources_view'
            ]
            
            for perm_type in user_permissions:
                permission, created = Permission.objects.get_or_create(
                    user=regular_user,
                    permission_type=perm_type,
                    defaults={
                        'granted': True,
                        'usu_cad': admin_user.email if admin_user else 'system',
                        'usu_atu': admin_user.email if admin_user else 'system'
                    }
                )
                if created:
                    print(f"   ✅ {regular_user.nome}: {perm_type}")
        
        # Viewer - apenas visualização
        if len(users) > 3:
            viewer_user = users[3]
            viewer_permissions = [
                'certificates_view', 'accounts_view', 'resources_view'
            ]
            
            for perm_type in viewer_permissions:
                permission, created = Permission.objects.get_or_create(
                    user=viewer_user,
                    permission_type=perm_type,
                    defaults={
                        'granted': True,
                        'usu_cad': admin_user.email if admin_user else 'system',
                        'usu_atu': admin_user.email if admin_user else 'system'
                    }
                )
                if created:
                    print(f"   ✅ {viewer_user.nome}: {perm_type}")
    
    # 4. Estatísticas finais
    print("\n📊 Estatísticas finais:")
    print(f"   • Roles criados: {Role.objects.count()}")
    print(f"   • Permissões criadas: {Permission.objects.count()}")
    print(f"   • Associações usuário-role: {UserRole.objects.count()}")
    print(f"   • Permissões concedidas: {Permission.objects.filter(granted=True).count()}")
    print(f"   • Permissões negadas: {Permission.objects.filter(granted=False).count()}")
    
    print("\n✅ Dados de demonstração criados com sucesso!")
    print("\n🌐 Acesse o sistema em: http://localhost:8000/permissions/")

if __name__ == '__main__':
    create_permissions_data() 