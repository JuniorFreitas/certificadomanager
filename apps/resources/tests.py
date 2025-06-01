from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from apps.accounts.models import Account
from .models import Resource
from .forms import ResourceForm, ResourceSearchForm
import json

User = get_user_model()


class ResourceModelTest(TestCase):
    """Testes para o modelo Resource"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            id='test-account',
            nome='Test Account',
            id_conta='123456789012',
            client='AKIATEST123456789012',
            secret='testsecret',
            usu_cad='test@example.com'
        )
    
    def test_create_resource(self):
        """Testa criação de recurso"""
        resource = Resource.objects.create(
            nome='Test S3 Bucket',
            tipo=0,  # S3
            url='https://test-bucket.s3.amazonaws.com',
            account=self.account,
            status=0,
            usu_cad='test@example.com'
        )
        
        self.assertEqual(resource.nome, 'Test S3 Bucket')
        self.assertEqual(resource.get_tipo_display(), 'S3')
        self.assertEqual(resource.get_status_display(), 'Ativo')
        self.assertTrue(resource.id)  # UUID gerado automaticamente
    
    def test_resource_str_representation(self):
        """Testa representação string do recurso"""
        resource = Resource.objects.create(
            nome='Test EC2',
            tipo=4,  # EC2
            url='https://ec2.amazonaws.com',
            account=self.account,
            usu_cad='test@example.com'
        )
        
        expected = f"Test EC2 (EC2)"
        self.assertEqual(str(resource), expected)
    
    def test_status_badge_class_property(self):
        """Testa propriedade status_badge_class"""
        resource = Resource.objects.create(
            nome='Test Resource',
            tipo=0,
            url='https://test.com',
            account=self.account,
            status=0,  # Ativo
            usu_cad='test@example.com'
        )
        
        self.assertEqual(resource.status_badge_class, 'bg-success')
        
        resource.status = 1  # Inativo
        self.assertEqual(resource.status_badge_class, 'bg-secondary')
        
        resource.status = 2  # Em Manutenção
        self.assertEqual(resource.status_badge_class, 'bg-warning')
    
    def test_tipo_icon_property(self):
        """Testa propriedade tipo_icon"""
        resource = Resource.objects.create(
            nome='Test S3',
            tipo=0,  # S3
            url='https://test.com',
            account=self.account,
            usu_cad='test@example.com'
        )
        
        self.assertEqual(resource.tipo_icon, 'bi-bucket')
        
        resource.tipo = 4  # EC2
        self.assertEqual(resource.tipo_icon, 'bi-server')
        
        resource.tipo = 5  # RDS
        self.assertEqual(resource.tipo_icon, 'bi-database')


class ResourceFormTest(TestCase):
    """Testes para o formulário ResourceForm"""
    
    def setUp(self):
        self.account = Account.objects.create(
            id='test-account',
            nome='Test Account',
            id_conta='123456789012',
            client='AKIATEST123456789012',
            secret='testsecret',
            usu_cad='test@example.com'
        )
    
    def test_valid_form(self):
        """Testa formulário válido"""
        form_data = {
            'nome': 'Test S3 Bucket',
            'tipo': 0,  # S3
            'url': 'https://test-bucket.s3.amazonaws.com',
            'account': self.account.id,
            'status': 0,
            'descricao': 'Test description'
        }
        
        form = ResourceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_url_format(self):
        """Testa URL inválida"""
        form_data = {
            'nome': 'Test Resource',
            'tipo': 0,
            'url': 'invalid-url',
            'account': self.account.id,
            'status': 0
        }
        
        form = ResourceForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Verifica se há erro de URL inválida (Django validation)
        self.assertIn('url', form.errors)
    
    def test_s3_url_validation(self):
        """Testa validação específica para URLs S3"""
        form_data = {
            'nome': 'Test S3',
            'tipo': 0,  # S3
            'url': 'https://example.com',  # Não contém 's3'
            'account': self.account.id,
            'status': 0
        }
        
        form = ResourceForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Verifica se há erro não-field (validação customizada)
        self.assertTrue(form.non_field_errors())
        error_text = str(form.non_field_errors())
        self.assertIn('s3', error_text.lower())
    
    def test_cloudfront_url_validation(self):
        """Testa validação específica para URLs CloudFront"""
        form_data = {
            'nome': 'Test CloudFront',
            'tipo': 2,  # CloudFront
            'url': 'https://example.com',  # Não contém 'cloudfront'
            'account': self.account.id,
            'status': 0
        }
        
        form = ResourceForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Verifica se há erro não-field (validação customizada)
        self.assertTrue(form.non_field_errors())
        error_text = str(form.non_field_errors())
        self.assertIn('cloudfront', error_text.lower())


class ResourceSearchFormTest(TestCase):
    """Testes para o formulário ResourceSearchForm"""
    
    def setUp(self):
        self.account = Account.objects.create(
            id='test-account',
            nome='Test Account',
            id_conta='123456789012',
            client='AKIATEST123456789012',
            secret='testsecret',
            usu_cad='test@example.com'
        )
    
    def test_empty_search_form(self):
        """Testa formulário de busca vazio"""
        form = ResourceSearchForm(data={})
        self.assertTrue(form.is_valid())
    
    def test_search_form_with_filters(self):
        """Testa formulário de busca com filtros"""
        form_data = {
            'search': 'test',
            'tipo': '0',
            'status': '0',
            'account': self.account.id
        }
        
        form = ResourceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search'], 'test')
        self.assertEqual(form.cleaned_data['tipo'], '0')


class ResourceViewTest(TestCase):
    """Testes para as views de Resource"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            id='test-account',
            nome='Test Account',
            id_conta='123456789012',
            client='AKIATEST123456789012',
            secret='testsecret',
            usu_cad='test@example.com'
        )
        
        self.resource = Resource.objects.create(
            nome='Test Resource',
            tipo=0,
            url='https://test-bucket.s3.amazonaws.com',
            account=self.account,
            usu_cad='test@example.com'
        )
        
        self.client.login(email='test@example.com', password='testpass123')
    
    def test_resource_list_view(self):
        """Testa view de listagem de recursos"""
        url = reverse('resources:list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resource')
        self.assertContains(response, 'Recursos')
    
    def test_resource_detail_view(self):
        """Testa view de detalhes do recurso"""
        url = reverse('resources:detail', kwargs={'resource_id': self.resource.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.resource.nome)
        self.assertContains(response, self.resource.url)
    
    def test_resource_create_view_get(self):
        """Testa view de criação (GET)"""
        url = reverse('resources:create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Recurso')
    
    def test_resource_create_view_post(self):
        """Testa view de criação (POST)"""
        url = reverse('resources:create')
        data = {
            'nome': 'New Resource',
            'tipo': 1,  # Load Balancer
            'url': 'https://test-lb.amazonaws.com',
            'account': self.account.id,
            'status': 0,
            'descricao': 'Test description'
        }
        
        response = self.client.post(url, data)
        
        # Deve redirecionar após criação bem-sucedida
        self.assertEqual(response.status_code, 302)
        
        # Verifica se o recurso foi criado
        self.assertTrue(Resource.objects.filter(nome='New Resource').exists())
    
    def test_resource_edit_view(self):
        """Testa view de edição"""
        url = reverse('resources:edit', kwargs={'resource_id': self.resource.id})
        data = {
            'nome': 'Updated Resource',
            'tipo': self.resource.tipo,
            'url': self.resource.url,
            'account': self.account.id,
            'status': 1,  # Mudando para Inativo
            'descricao': 'Updated description'
        }
        
        response = self.client.post(url, data)
        
        # Deve redirecionar após edição bem-sucedida
        self.assertEqual(response.status_code, 302)
        
        # Verifica se o recurso foi atualizado
        updated_resource = Resource.objects.get(id=self.resource.id)
        self.assertEqual(updated_resource.nome, 'Updated Resource')
        self.assertEqual(updated_resource.status, 1)
    
    def test_resource_delete_view_get(self):
        """Testa view de exclusão (GET)"""
        url = reverse('resources:delete', kwargs={'resource_id': self.resource.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmar Exclusão')
        self.assertContains(response, self.resource.nome)
    
    def test_resource_delete_view_post(self):
        """Testa view de exclusão (POST)"""
        url = reverse('resources:delete', kwargs={'resource_id': self.resource.id})
        response = self.client.post(url)
        
        # Deve redirecionar após exclusão
        self.assertEqual(response.status_code, 302)
        
        # Verifica se o recurso foi excluído
        self.assertFalse(Resource.objects.filter(id=self.resource.id).exists())
    
    def test_resource_list_with_search(self):
        """Testa listagem com busca"""
        url = reverse('resources:list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resource')
    
    def test_resource_list_with_filters(self):
        """Testa listagem com filtros"""
        url = reverse('resources:list')
        response = self.client.get(url, {
            'tipo': '0',
            'status': '0',
            'account': self.account.id
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resource')
    
    @patch('apps.resources.views.boto3.Session')
    def test_test_connection_view_success(self, mock_session):
        """Testa view de teste de conexão (sucesso)"""
        # Mock da resposta do AWS STS
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {
            'Account': '123456789012',
            'UserId': 'AIDACKCEVSQ6C2EXAMPLE',
            'Arn': 'arn:aws:iam::123456789012:user/test'
        }
        mock_session.return_value.client.return_value = mock_sts
        
        url = reverse('resources:test_connection', kwargs={'resource_id': self.resource.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('Conexão testada com sucesso', data['message'])
    
    @patch('apps.resources.views.boto3.Session')
    def test_test_connection_view_failure(self, mock_session):
        """Testa view de teste de conexão (falha)"""
        # Mock de erro
        mock_session.side_effect = Exception('Connection failed')
        
        url = reverse('resources:test_connection', kwargs={'resource_id': self.resource.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Connection failed', data['message'])
    
    def test_unauthorized_access(self):
        """Testa acesso não autorizado"""
        self.client.logout()
        
        url = reverse('resources:list')
        response = self.client.get(url)
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class ResourceIntegrationTest(TestCase):
    """Testes de integração para recursos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            id='test-account',
            nome='Test Account',
            id_conta='123456789012',
            client='AKIATEST123456789012',
            secret='testsecret',
            usu_cad='test@example.com'
        )
    
    def test_resource_account_relationship(self):
        """Testa relacionamento entre Resource e Account"""
        resource = Resource.objects.create(
            nome='Test Resource',
            tipo=0,
            url='https://test.s3.amazonaws.com',
            account=self.account,
            usu_cad='test@example.com'
        )
        
        # Testa acesso ao account através do resource
        self.assertEqual(resource.account.nome, 'Test Account')
        self.assertEqual(resource.account.id_conta, '123456789012')
        
        # Testa acesso aos resources através do account
        account_resources = self.account.resource_set.all()
        self.assertIn(resource, account_resources)
    
    def test_cascade_delete(self):
        """Testa exclusão em cascata"""
        resource = Resource.objects.create(
            nome='Test Resource',
            tipo=0,
            url='https://test.s3.amazonaws.com',
            account=self.account,
            usu_cad='test@example.com'
        )
        
        resource_id = resource.id
        
        # Exclui a conta
        self.account.delete()
        
        # Verifica se o recurso também foi excluído
        self.assertFalse(Resource.objects.filter(id=resource_id).exists())
    
    @patch('apps.resources.views._get_resource_aws_info')
    def test_aws_info_integration(self, mock_aws_info):
        """Testa integração com informações AWS"""
        mock_aws_info.return_value = {
            'account_id': '123456789012',
            'region': 'us-east-1',
            'status': 'accessible',
            'service': 'S3'
        }
        
        resource = Resource.objects.create(
            nome='Test S3',
            tipo=0,
            url='https://test.s3.amazonaws.com',
            account=self.account,
            usu_cad='test@example.com'
        )
        
        client = Client()
        client.force_login(self.user)
        
        url = reverse('resources:detail', kwargs={'resource_id': resource.id})
        response = client.get(url)
        
        self.assertEqual(response.status_code, 200)
        mock_aws_info.assert_called_once_with(resource)
