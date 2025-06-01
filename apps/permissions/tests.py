from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch
import json
from .models import Permission, Role, UserRole
from .forms import PermissionForm, RoleForm, UserRoleForm, PermissionSearchForm, BulkPermissionForm

User = get_user_model()


class PermissionModelTest(TestCase):
    """Testes para o modelo Permission"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
    
    def test_permission_creation(self):
        """Testa criação de permissão"""
        permission = Permission.objects.create(
            user=self.user,
            permission_type='users_create',
            granted=True,
            usu_cad='admin@test.com'
        )
        
        self.assertEqual(permission.user, self.user)
        self.assertEqual(permission.permission_type, 'users_create')
        self.assertTrue(permission.granted)
        self.assertIsNotNone(permission.id)
    
    def test_permission_str_method(self):
        """Testa método __str__ da permissão"""
        permission = Permission.objects.create(
            user=self.user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        
        expected = f"{self.user.nome} - Criar Usuários"
        self.assertEqual(str(permission), expected)
    
    def test_permission_unique_constraint(self):
        """Testa constraint de unicidade user + permission_type"""
        Permission.objects.create(
            user=self.user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        
        with self.assertRaises(IntegrityError):
            Permission.objects.create(
                user=self.user,
                permission_type='users_create',
                usu_cad='admin@test.com'
            )
    
    def test_permission_properties(self):
        """Testa propriedades do modelo Permission"""
        permission = Permission.objects.create(
            user=self.user,
            permission_type='users_create',
            granted=True,
            usu_cad='admin@test.com'
        )
        
        self.assertEqual(permission.module_name, 'Users')
        self.assertEqual(permission.action_name, 'Create')
        self.assertEqual(permission.status_badge_class, 'bg-success')
        
        permission.granted = False
        self.assertEqual(permission.status_badge_class, 'bg-danger')


class RoleModelTest(TestCase):
    """Testes para o modelo Role"""
    
    def test_role_creation(self):
        """Testa criação de role"""
        role = Role.objects.create(
            name='admin',
            description='Administrador do sistema',
            usu_cad='admin@test.com'
        )
        
        self.assertEqual(role.name, 'admin')
        self.assertEqual(role.description, 'Administrador do sistema')
        self.assertTrue(role.is_active)
        self.assertIsNotNone(role.id)
    
    def test_role_str_method(self):
        """Testa método __str__ do role"""
        role = Role.objects.create(
            name='admin',
            usu_cad='admin@test.com'
        )
        
        self.assertEqual(str(role), 'Administrador')
    
    def test_role_badge_class_property(self):
        """Testa propriedade badge_class do role"""
        role_admin = Role.objects.create(name='admin', usu_cad='admin@test.com')
        role_manager = Role.objects.create(name='manager', usu_cad='admin@test.com')
        role_user = Role.objects.create(name='user', usu_cad='admin@test.com')
        role_viewer = Role.objects.create(name='viewer', usu_cad='admin@test.com')
        
        self.assertEqual(role_admin.badge_class, 'bg-danger')
        self.assertEqual(role_manager.badge_class, 'bg-warning')
        self.assertEqual(role_user.badge_class, 'bg-primary')
        self.assertEqual(role_viewer.badge_class, 'bg-secondary')
    
    def test_role_unique_name(self):
        """Testa constraint de unicidade do nome do role"""
        Role.objects.create(name='admin', usu_cad='admin@test.com')
        
        with self.assertRaises(IntegrityError):
            Role.objects.create(name='admin', usu_cad='admin@test.com')


class UserRoleModelTest(TestCase):
    """Testes para o modelo UserRole"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        self.role = Role.objects.create(
            name='admin',
            usu_cad='admin@test.com'
        )
    
    def test_user_role_creation(self):
        """Testa criação de associação usuário-role"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            usu_cad='admin@test.com'
        )
        
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertTrue(user_role.is_active)
        self.assertIsNotNone(user_role.id)
    
    def test_user_role_str_method(self):
        """Testa método __str__ da associação"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            usu_cad='admin@test.com'
        )
        
        expected = f"{self.user.nome} - Administrador"
        self.assertEqual(str(user_role), expected)
    
    def test_user_role_unique_constraint(self):
        """Testa constraint de unicidade user + role"""
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            usu_cad='admin@test.com'
        )
        
        with self.assertRaises(IntegrityError):
            UserRole.objects.create(
                user=self.user,
                role=self.role,
                usu_cad='admin@test.com'
            )


class PermissionFormTest(TestCase):
    """Testes para o formulário PermissionForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
    
    def test_permission_form_valid(self):
        """Testa formulário válido"""
        form_data = {
            'user': self.user.id,
            'permission_type': 'users_create',
            'granted': True
        }
        form = PermissionForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_permission_form_duplicate_validation(self):
        """Testa validação de duplicata"""
        Permission.objects.create(
            user=self.user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        
        form_data = {
            'user': self.user.id,
            'permission_type': 'users_create',
            'granted': True
        }
        form = PermissionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Já existe uma permissão', str(form.errors))


class RoleFormTest(TestCase):
    """Testes para o formulário RoleForm"""
    
    def test_role_form_valid(self):
        """Testa formulário válido"""
        form_data = {
            'name': 'admin',
            'description': 'Administrador do sistema',
            'is_active': True
        }
        form = RoleForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_role_form_required_fields(self):
        """Testa campos obrigatórios"""
        form = RoleForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class PermissionViewTest(TestCase):
    """Testes para as views de permissões"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='adminpass123'
        )
        self.test_user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
    
    def test_permission_list_view(self):
        """Testa view de listagem de permissões"""
        response = self.client.get(reverse('permissions:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Permissões')
    
    def test_permission_create_view_get(self):
        """Testa view de criação de permissão (GET)"""
        response = self.client.get(reverse('permissions:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Permissão')
    
    def test_permission_create_view_post(self):
        """Testa view de criação de permissão (POST)"""
        data = {
            'user': self.test_user.id,
            'permission_type': 'users_create',
            'granted': True
        }
        response = self.client.post(reverse('permissions:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Permission.objects.filter(user=self.test_user).exists())
    
    def test_permission_detail_view(self):
        """Testa view de detalhes de permissão"""
        permission = Permission.objects.create(
            user=self.test_user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        response = self.client.get(reverse('permissions:detail', args=[permission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, permission.get_permission_type_display())
    
    def test_permission_edit_view(self):
        """Testa view de edição de permissão"""
        permission = Permission.objects.create(
            user=self.test_user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        
        data = {
            'user': self.test_user.id,
            'permission_type': 'users_edit',
            'granted': False
        }
        response = self.client.post(reverse('permissions:edit', args=[permission.id]), data)
        self.assertEqual(response.status_code, 302)
        
        permission.refresh_from_db()
        self.assertEqual(permission.permission_type, 'users_edit')
        self.assertFalse(permission.granted)
    
    def test_permission_delete_view(self):
        """Testa view de exclusão de permissão"""
        permission = Permission.objects.create(
            user=self.test_user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        
        response = self.client.post(reverse('permissions:delete', args=[permission.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Permission.objects.filter(id=permission.id).exists())


class RoleViewTest(TestCase):
    """Testes para as views de roles"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='adminpass123'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
    
    def test_role_list_view(self):
        """Testa view de listagem de roles"""
        response = self.client.get(reverse('permissions:role_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Roles')
    
    def test_role_create_view_post(self):
        """Testa view de criação de role (POST)"""
        data = {
            'name': 'admin',
            'description': 'Administrador do sistema',
            'is_active': True
        }
        response = self.client.post(reverse('permissions:role_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Role.objects.filter(name='admin').exists())


class AjaxViewTest(TestCase):
    """Testes para views AJAX"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='adminpass123'
        )
        self.test_user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
    
    def test_get_user_permissions_ajax(self):
        """Testa endpoint AJAX para obter permissões do usuário"""
        permission = Permission.objects.create(
            user=self.test_user,
            permission_type='users_create',
            usu_cad='admin@test.com'
        )
        
        response = self.client.get(
            reverse('permissions:get_user_permissions', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['permissions']), 1)
        self.assertEqual(data['permissions'][0]['type'], 'users_create')
    
    def test_toggle_permission_ajax(self):
        """Testa endpoint AJAX para alternar status de permissão"""
        permission = Permission.objects.create(
            user=self.test_user,
            permission_type='users_create',
            granted=True,
            usu_cad='admin@test.com'
        )
        
        response = self.client.post(
            reverse('permissions:toggle_permission', args=[permission.id]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(data['granted'])
        
        permission.refresh_from_db()
        self.assertFalse(permission.granted)


class BulkPermissionTest(TestCase):
    """Testes para concessão em lote de permissões"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='adminpass123'
        )
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            nome='User 1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            nome='User 2',
            password='testpass123'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
    
    def test_bulk_permission_form_valid(self):
        """Testa formulário de concessão em lote"""
        form_data = {
            'users': [self.user1.id, self.user2.id],
            'permissions': ['users_create', 'users_view'],
            'granted': True
        }
        form = BulkPermissionForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_bulk_permission_view(self):
        """Testa view de concessão em lote"""
        data = {
            'users': [self.user1.id, self.user2.id],
            'permissions': ['users_create', 'users_view'],
            'granted': True
        }
        response = self.client.post(reverse('permissions:bulk'), data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se as permissões foram criadas
        self.assertEqual(Permission.objects.count(), 4)  # 2 usuários x 2 permissões
        self.assertTrue(
            Permission.objects.filter(
                user=self.user1, 
                permission_type='users_create',
                granted=True
            ).exists()
        )


class PermissionSearchTest(TestCase):
    """Testes para busca de permissões"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='adminpass123'
        )
        self.test_user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
        
        Permission.objects.create(
            user=self.test_user,
            permission_type='users_create',
            granted=True,
            usu_cad='admin@test.com'
        )
    
    def test_search_by_user_name(self):
        """Testa busca por nome do usuário"""
        response = self.client.get(reverse('permissions:list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_search_by_permission_type(self):
        """Testa busca por tipo de permissão"""
        response = self.client.get(reverse('permissions:list'), {'permission_type': 'users_create'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Usuários')
    
    def test_search_by_granted_status(self):
        """Testa busca por status de concessão"""
        response = self.client.get(reverse('permissions:list'), {'granted': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Concedida')


class PermissionIntegrationTest(TestCase):
    """Testes de integração do módulo de permissões"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            nome='Admin User',
            password='adminpass123'
        )
        self.client.login(email='admin@example.com', password='adminpass123')
    
    def test_complete_permission_workflow(self):
        """Testa fluxo completo de gerenciamento de permissões"""
        # 1. Criar role
        role_data = {
            'name': 'admin',
            'description': 'Administrador do sistema',
            'is_active': True
        }
        response = self.client.post(reverse('permissions:role_create'), role_data)
        self.assertEqual(response.status_code, 302)
        role = Role.objects.get(name='admin')
        
        # 2. Criar usuário
        user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        # 3. Associar usuário ao role
        user_role_data = {
            'user': user.id,
            'role': role.id,
            'is_active': True
        }
        response = self.client.post(reverse('permissions:user_role_create'), user_role_data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Criar permissão
        permission_data = {
            'user': user.id,
            'permission_type': 'users_create',
            'granted': True
        }
        response = self.client.post(reverse('permissions:create'), permission_data)
        self.assertEqual(response.status_code, 302)
        
        # 5. Verificar se tudo foi criado corretamente
        self.assertTrue(Role.objects.filter(name='admin').exists())
        self.assertTrue(UserRole.objects.filter(user=user, role=role).exists())
        self.assertTrue(Permission.objects.filter(user=user, permission_type='users_create').exists())
        
        # 6. Testar alteração via AJAX
        permission = Permission.objects.get(user=user, permission_type='users_create')
        response = self.client.post(
            reverse('permissions:toggle_permission', args=[permission.id]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        permission.refresh_from_db()
        self.assertFalse(permission.granted)
