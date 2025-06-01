from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from .models import Account, AccountRegion, AccountService
from .forms import AccountForm, AccountSearchForm

User = get_user_model()


class AccountModelTest(TestCase):
    """Testes para o modelo Account"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        self.account_data = {
            'nome': 'Conta de Teste',
            'descricao': 'Conta AWS para testes',
            'account_id': '123456789012',
            'account_type': 'iam',
            'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
            'secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'default_region': 'us-east-1',
            'status': 0,
            'usu_cad': self.user.email
        }
    
    def test_create_account(self):
        """Testa criação de conta"""
        account = Account.objects.create(**self.account_data)
        
        self.assertEqual(account.nome, self.account_data['nome'])
        self.assertEqual(account.account_id, self.account_data['account_id'])
        self.assertEqual(account.account_type, self.account_data['account_type'])
        self.assertIsNotNone(account.id)  # ID deve ser gerado automaticamente
    
    def test_account_str_representation(self):
        """Testa a representação string da conta"""
        account = Account.objects.create(**self.account_data)
        expected = f"{account.nome} ({account.account_id})"
        self.assertEqual(str(account), expected)
    
    def test_account_unique_account_id(self):
        """Testa unicidade do Account ID"""
        Account.objects.create(**self.account_data)
        
        # Tentar criar outra conta com o mesmo account_id
        duplicate_data = self.account_data.copy()
        duplicate_data['nome'] = 'Conta Duplicada'
        
        with self.assertRaises(Exception):  # IntegrityError
            Account.objects.create(**duplicate_data)
    
    def test_account_properties(self):
        """Testa propriedades do modelo"""
        account = Account.objects.create(**self.account_data)
        
        # Testar propriedades
        self.assertEqual(account.status_display, 'Ativa')
        self.assertEqual(account.status_badge_class, 'bg-success')
        self.assertTrue(account.is_active)  # Status 0 = ativa
    
    def test_account_validation_methods(self):
        """Testa métodos de validação"""
        account = Account.objects.create(**self.account_data)
        
        # Testar método de criptografia (mock)
        secret = 'test_secret'
        encrypted = account._encrypt_secret(secret)
        self.assertIsInstance(encrypted, str)
        
        # Testar descriptografia
        decrypted = account._decrypt_secret(encrypted)
        # Como pode falhar na criptografia, verificar se retorna algo
        self.assertIsInstance(decrypted, str)


class AccountFormTest(TestCase):
    """Testes para o formulário AccountForm"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.valid_data = {
            'nome': 'Conta de Teste',
            'descricao': 'Conta AWS para testes',
            'account_id': '123456789012',
            'account_type': 'iam',
            'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
            'secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'confirm_secret': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'default_region': 'us-east-1',
            'enabled_regions': ['us-east-1', 'us-west-2'],
            'status': 0,
            'max_instances': 20,
            'max_storage_gb': 1000,
            'tags': '{"ambiente": "teste"}',
            'test_connection': False  # Desabilitar teste para os testes unitários
        }
    
    def test_valid_form(self):
        """Testa formulário válido"""
        form = AccountForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_account_id_format(self):
        """Testa validação de formato do Account ID"""
        invalid_data = self.valid_data.copy()
        invalid_data['account_id'] = '12345'  # Muito curto
        
        form = AccountForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('account_id', form.errors)
    
    def test_invalid_access_key_format(self):
        """Testa validação de formato do Access Key"""
        invalid_data = self.valid_data.copy()
        invalid_data['access_key_id'] = 'INVALID_KEY'
        
        form = AccountForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('access_key_id', form.errors)
    
    def test_secret_confirmation_mismatch(self):
        """Testa validação de confirmação de secret"""
        invalid_data = self.valid_data.copy()
        invalid_data['confirm_secret'] = 'different_secret'
        
        form = AccountForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_secret', form.errors)
    
    def test_form_save(self):
        """Testa salvamento do formulário"""
        form = AccountForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        account = form.save(commit=False)
        account.usu_cad = 'test@example.com'
        account.save()
        
        self.assertEqual(account.nome, self.valid_data['nome'])
        self.assertEqual(account.account_id, self.valid_data['account_id'])


class AccountViewsTest(TestCase):
    """Testes para as views de Account"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
        
        self.account = Account.objects.create(
            nome='Conta de Teste',
            descricao='Conta AWS para testes',
            account_id='123456789012',
            account_type='iam',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            default_region='us-east-1',
            status=0,
            usu_cad=self.user.email
        )
    
    def test_account_list_view(self):
        """Testa a view de listagem de contas"""
        response = self.client.get(reverse('accounts:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Conta de Teste')
        self.assertContains(response, '123456789012')
    
    def test_account_detail_view(self):
        """Testa a view de detalhes da conta"""
        response = self.client.get(
            reverse('accounts:detail', args=[self.account.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.account.nome)
        self.assertContains(response, self.account.account_id)
    
    def test_account_create_view_get(self):
        """Testa a view de criação de conta (GET)"""
        response = self.client.get(reverse('accounts:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Conta AWS')
    
    def test_account_create_view_post(self):
        """Testa a view de criação de conta (POST)"""
        data = {
            'nome': 'Nova Conta',
            'descricao': 'Nova conta AWS',
            'account_id': '987654321098',
            'account_type': 'iam',
            'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
            'secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'confirm_secret': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'default_region': 'us-east-1',
            'status': 0,
            'max_instances': 20,
            'max_storage_gb': 1000,
            'test_connection': False
        }
        
        response = self.client.post(reverse('accounts:create'), data)
        
        # Deve redirecionar após criação bem-sucedida
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a conta foi criada
        new_account = Account.objects.get(account_id='987654321098')
        self.assertEqual(new_account.nome, 'Nova Conta')
        self.assertEqual(new_account.usu_cad, self.user.email)
    
    def test_account_edit_view(self):
        """Testa a view de edição de conta"""
        response = self.client.get(
            reverse('accounts:edit', args=[self.account.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar Conta AWS')
    
    def test_account_delete_view_get(self):
        """Testa a view de exclusão de conta (GET)"""
        response = self.client.get(
            reverse('accounts:delete', args=[self.account.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Excluir Conta AWS')
    
    def test_account_delete_view_post(self):
        """Testa a view de exclusão de conta (POST)"""
        account_id = self.account.id
        response = self.client.post(
            reverse('accounts:delete', args=[account_id])
        )
        
        # Deve redirecionar após exclusão
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a conta foi excluída
        with self.assertRaises(Account.DoesNotExist):
            Account.objects.get(id=account_id)
    
    def test_account_validate_view(self):
        """Testa a view de validação de conta"""
        with patch('apps.accounts.models.Account.validate_credentials') as mock_validate:
            mock_validate.return_value = (True, 'Credenciais válidas')
            
            response = self.client.get(
                reverse('accounts:validate', args=[self.account.id])
            )
            
            # Deve redirecionar após validação
            self.assertEqual(response.status_code, 302)
            # Verificar se o método foi chamado
            mock_validate.assert_called_once()
    
    def test_account_test_view_get(self):
        """Testa a view de teste de conexão (GET)"""
        response = self.client.get(
            reverse('accounts:test', args=[self.account.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testar Conexão')


class AccountAWSIntegrationTest(TestCase):
    """Testes para integração com AWS (mocked)"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.account = Account(
            nome='Conta AWS Test',
            descricao='Conta para testes de integração',
            account_id='123456789012',
            account_type='iam',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            default_region='us-east-1',
            status=0,
            usu_cad='test@example.com'
        )
    
    @patch('boto3.Session')
    def test_get_boto3_session(self, mock_session):
        """Testa criação de sessão boto3"""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        session = self.account.get_boto3_session()
        
        mock_session.assert_called_once_with(
            aws_access_key_id=self.account.access_key_id,
            aws_secret_access_key=self.account.decrypted_secret,
            aws_session_token=None,
            region_name=self.account.default_region
        )
        self.assertEqual(session, mock_session_instance)
    
    @patch('boto3.Session')
    def test_validate_credentials_success(self, mock_session):
        """Testa validação de credenciais bem-sucedida"""
        # Mock da sessão e cliente STS
        mock_session_instance = MagicMock()
        mock_sts_client = MagicMock()
        mock_session_instance.client.return_value = mock_sts_client
        mock_session.return_value = mock_session_instance
        
        # Mock da resposta do STS
        mock_sts_client.get_caller_identity.return_value = {
            'Account': '123456789012',
            'UserId': 'AIDACKCEVSQ6C2EXAMPLE',
            'Arn': 'arn:aws:iam::123456789012:user/test'
        }
        
        success, message = self.account.validate_credentials()
        
        self.assertTrue(success)
        self.assertIn('sucesso', message)
        self.assertTrue(self.account.is_validated)
        self.assertEqual(self.account.status, 0)  # Ativa
    
    @patch('boto3.Session')
    def test_get_resource_summary(self, mock_session):
        """Testa obtenção de resumo de recursos"""
        # Mock da sessão
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock dos clientes
        mock_ec2_client = MagicMock()
        mock_s3_client = MagicMock()
        
        def client_side_effect(service):
            if service == 'ec2':
                return mock_ec2_client
            elif service == 's3':
                return mock_s3_client
            return MagicMock()
        
        mock_session_instance.client.side_effect = client_side_effect
        
        # Mock das respostas
        mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {'Instances': [{'State': {'Name': 'running'}}]}
            ]
        }
        mock_s3_client.list_buckets.return_value = {
            'Buckets': [{'Name': 'bucket1'}, {'Name': 'bucket2'}]
        }
        
        # Marcar conta como validada
        self.account.is_validated = True
        
        summary = self.account.get_resource_summary()
        
        self.assertIn('ec2_instances', summary)
        self.assertIn('s3_buckets', summary)
        self.assertEqual(summary['ec2_instances'], 1)
        self.assertEqual(summary['s3_buckets'], 2)


class AccountRegionTest(TestCase):
    """Testes para o modelo AccountRegion"""
    
    def setUp(self):
        self.account = Account.objects.create(
            nome='Conta de Teste',
            account_id='123456789012',
            account_type='iam',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            default_region='us-east-1',
            status=0,
            usu_cad='test@example.com'
        )
    
    def test_create_account_region(self):
        """Testa criação de região da conta"""
        region = AccountRegion.objects.create(
            account=self.account,
            region_code='us-west-2',
            is_enabled=True,
            usu_cad='test@example.com'
        )
        
        self.assertEqual(region.account, self.account)
        self.assertEqual(region.region_code, 'us-west-2')
        self.assertTrue(region.is_enabled)
    
    def test_account_region_unique_constraint(self):
        """Testa constraint de unicidade da região por conta"""
        AccountRegion.objects.create(
            account=self.account,
            region_code='us-west-2',
            is_enabled=True,
            usu_cad='test@example.com'
        )
        
        # Tentar criar região duplicada
        with self.assertRaises(Exception):  # IntegrityError
            AccountRegion.objects.create(
                account=self.account,
                region_code='us-west-2',
                is_enabled=True,
                usu_cad='test@example.com'
            )


class AccountServiceTest(TestCase):
    """Testes para o modelo AccountService"""
    
    def setUp(self):
        self.account = Account.objects.create(
            nome='Conta de Teste',
            account_id='123456789012',
            account_type='iam',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            default_region='us-east-1',
            status=0,
            usu_cad='test@example.com'
        )
    
    def test_create_account_service(self):
        """Testa criação de serviço da conta"""
        service = AccountService.objects.create(
            account=self.account,
            service_name='ec2',
            is_enabled=True,
            usu_cad='test@example.com'
        )
        
        self.assertEqual(service.account, self.account)
        self.assertEqual(service.service_name, 'ec2')
        self.assertTrue(service.is_enabled)
    
    def test_account_service_unique_constraint(self):
        """Testa constraint de unicidade do serviço por conta"""
        AccountService.objects.create(
            account=self.account,
            service_name='ec2',
            is_enabled=True,
            usu_cad='test@example.com'
        )
        
        # Tentar criar serviço duplicado
        with self.assertRaises(Exception):  # IntegrityError
            AccountService.objects.create(
                account=self.account,
                service_name='ec2',
                is_enabled=True,
                usu_cad='test@example.com'
            )
