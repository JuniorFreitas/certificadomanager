import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTest(TestCase):
    """Testes para o modelo User"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user_data = {
            'email': 'test@example.com',
            'nome': 'Test User',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Testa criação de usuário comum"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.nome, self.user_data['nome'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.status, 0)  # Ativo por padrão
        self.assertIsNotNone(user.id)  # ID deve ser gerado automaticamente
    
    def test_create_superuser(self):
        """Testa criação de superusuário"""
        user = User.objects.create_superuser(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.nome, self.user_data['nome'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.status, 0)
    
    def test_create_user_without_email(self):
        """Testa que não é possível criar usuário sem email"""
        user_data = self.user_data.copy()
        del user_data['email']
        
        with self.assertRaises(TypeError):
            User.objects.create_user(**user_data)
    
    def test_create_user_without_nome(self):
        """Testa que não é possível criar usuário sem nome"""
        user_data = self.user_data.copy()
        del user_data['nome']
        
        with self.assertRaises(TypeError):
            User.objects.create_user(**user_data)
    
    def test_user_str_representation(self):
        """Testa a representação string do usuário"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.nome} ({user.email})"
        self.assertEqual(str(user), expected)
    
    def test_email_normalization(self):
        """Testa normalização do email"""
        user_data = self.user_data.copy()
        user_data['email'] = 'Test@EXAMPLE.COM'
        
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.email, 'Test@example.com')
    
    def test_unique_email_constraint(self):
        """Testa que emails devem ser únicos"""
        User.objects.create_user(**self.user_data)
        
        # Tentar criar outro usuário com mesmo email deve falhar
        user_data2 = self.user_data.copy()
        user_data2['nome'] = 'Another User'
        
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(**user_data2)


@pytest.mark.django_db
class UserModelPytestTest:
    """Testes usando pytest para o modelo User"""
    
    def test_user_creation_with_pytest(self):
        """Teste de criação de usuário usando pytest"""
        user = User.objects.create_user(
            email='pytest@example.com',
            nome='Pytest User',
            password='testpass123'
        )
        
        assert user.email == 'pytest@example.com'
        assert user.nome == 'Pytest User'
        assert user.check_password('testpass123')
        assert not user.is_staff
        assert not user.is_superuser
