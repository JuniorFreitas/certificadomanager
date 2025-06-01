from django.test import TestCase
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from .models import Certificate
from .forms import CertificateForm

User = get_user_model()


class CertificateModelTest(TestCase):
    """Testes para o modelo Certificate"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        self.certificate_data = {
            'versao': 'v3',
            'num_serie': '123456789',
            'alg_assin': 'SHA256withRSA',
            'alg_hash_assin': 'SHA256',
            'emissor': 'Test CA',
            'valid_ini': date.today(),
            'valid_fim': date.today() + timedelta(days=365),
            'requerente': 'Test Company',
            'chave_pub': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
            'chave_pub_param': 'RSA 2048 bits',
            'status': 0,
            'arquivo': b'test certificate content',
            'usu_cad': self.user.email
        }
    
    def test_create_certificate(self):
        """Testa criação de certificado"""
        certificate = Certificate.objects.create(**self.certificate_data)
        
        self.assertEqual(certificate.versao, self.certificate_data['versao'])
        self.assertEqual(certificate.num_serie, self.certificate_data['num_serie'])
        self.assertEqual(certificate.requerente, self.certificate_data['requerente'])
        self.assertEqual(certificate.status, 0)
        self.assertIsNotNone(certificate.id)  # ID deve ser gerado automaticamente
    
    def test_certificate_str_representation(self):
        """Testa a representação string do certificado"""
        certificate = Certificate.objects.create(**self.certificate_data)
        expected = f"{certificate.requerente} - {certificate.num_serie}"
        self.assertEqual(str(certificate), expected)
    
    def test_is_expired_property(self):
        """Testa a propriedade is_expired"""
        # Certificado válido
        certificate = Certificate.objects.create(**self.certificate_data)
        self.assertFalse(certificate.is_expired)
        
        # Certificado expirado
        expired_data = self.certificate_data.copy()
        expired_data['valid_fim'] = date.today() - timedelta(days=1)
        expired_data['num_serie'] = '987654321'
        expired_certificate = Certificate.objects.create(**expired_data)
        self.assertTrue(expired_certificate.is_expired)
    
    def test_days_until_expiry_property(self):
        """Testa a propriedade days_until_expiry"""
        certificate = Certificate.objects.create(**self.certificate_data)
        expected_days = (certificate.valid_fim - date.today()).days
        self.assertEqual(certificate.days_until_expiry, expected_days)
        
        # Certificado expirado deve retornar 0
        expired_data = self.certificate_data.copy()
        expired_data['valid_fim'] = date.today() - timedelta(days=1)
        expired_data['num_serie'] = '987654321'
        expired_certificate = Certificate.objects.create(**expired_data)
        self.assertEqual(expired_certificate.days_until_expiry, 0)


class CertificateFormTest(TestCase):
    """Testes para o formulário CertificateForm"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.valid_data = {
            'versao': 'v3',
            'num_serie': '123456789',
            'alg_assin': 'SHA256withRSA',
            'alg_hash_assin': 'SHA256',
            'emissor': 'Test CA',
            'valid_ini': date.today(),
            'valid_fim': date.today() + timedelta(days=365),
            'requerente': 'Test Company',
            'chave_pub': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
            'chave_pub_param': 'RSA 2048 bits',
            'status': 0,
        }
        
        self.file_data = {
            'arquivo_upload': SimpleUploadedFile(
                "test.crt", 
                b"test certificate content", 
                content_type="application/x-x509-ca-cert"
            )
        }
    
    def test_valid_form(self):
        """Testa formulário válido"""
        form = CertificateForm(data=self.valid_data, files=self.file_data)
        self.assertTrue(form.is_valid())
    
    def test_form_save_with_file(self):
        """Testa salvamento do formulário com arquivo"""
        form = CertificateForm(data=self.valid_data, files=self.file_data)
        self.assertTrue(form.is_valid())
        
        certificate = form.save(commit=False)
        certificate.usu_cad = 'test@example.com'
        certificate.save()
        
        self.assertEqual(certificate.arquivo, b"test certificate content")
        self.assertEqual(certificate.requerente, self.valid_data['requerente'])


class CertificateViewsTest(TestCase):
    """Testes para as views de Certificate"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
        
        self.certificate = Certificate.objects.create(
            versao='v3',
            num_serie='123456789',
            alg_assin='SHA256withRSA',
            alg_hash_assin='SHA256',
            emissor='Test CA',
            valid_ini=date.today(),
            valid_fim=date.today() + timedelta(days=365),
            requerente='Test Company',
            chave_pub='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
            chave_pub_param='RSA 2048 bits',
            status=0,
            arquivo=b'test certificate content',
            usu_cad=self.user.email
        )
    
    def test_certificate_list_view(self):
        """Testa a view de listagem de certificados"""
        response = self.client.get(reverse('certificates:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Company')
        self.assertContains(response, '123456789')
    
    def test_certificate_detail_view(self):
        """Testa a view de detalhes do certificado"""
        response = self.client.get(
            reverse('certificates:detail', args=[self.certificate.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.certificate.requerente)
        self.assertContains(response, self.certificate.num_serie)
    
    def test_certificate_create_view_get(self):
        """Testa a view de criação de certificado (GET)"""
        response = self.client.get(reverse('certificates:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Certificado')
    
    def test_certificate_create_view_post(self):
        """Testa a view de criação de certificado (POST)"""
        data = {
            'versao': 'v3',
            'num_serie': '987654321',
            'alg_assin': 'SHA256withRSA',
            'alg_hash_assin': 'SHA256',
            'emissor': 'New Test CA',
            'valid_ini': date.today(),
            'valid_fim': date.today() + timedelta(days=365),
            'requerente': 'New Test Company',
            'chave_pub': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
            'chave_pub_param': 'RSA 2048 bits',
            'status': 0,
        }
        
        file_data = {
            'arquivo_upload': SimpleUploadedFile(
                "new_test.crt", 
                b"new test certificate content", 
                content_type="application/x-x509-ca-cert"
            )
        }
        
        response = self.client.post(
            reverse('certificates:create'), 
            data={**data, **file_data}
        )
        
        # Deve redirecionar após criação bem-sucedida
        self.assertEqual(response.status_code, 302)
        
        # Verifica se o certificado foi criado
        new_certificate = Certificate.objects.get(num_serie='987654321')
        self.assertEqual(new_certificate.requerente, 'New Test Company')
        self.assertEqual(new_certificate.usu_cad, self.user.email)
    
    def test_certificate_edit_view(self):
        """Testa a view de edição de certificado"""
        response = self.client.get(
            reverse('certificates:edit', args=[self.certificate.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar Certificado')
    
    def test_certificate_delete_view_get(self):
        """Testa a view de exclusão de certificado (GET)"""
        response = self.client.get(
            reverse('certificates:delete', args=[self.certificate.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmar Exclusão')
    
    def test_certificate_delete_view_post(self):
        """Testa a view de exclusão de certificado (POST)"""
        certificate_id = self.certificate.id
        response = self.client.post(
            reverse('certificates:delete', args=[certificate_id])
        )
        
        # Deve redirecionar após exclusão
        self.assertEqual(response.status_code, 302)
        
        # Verifica se o certificado foi excluído
        with self.assertRaises(Certificate.DoesNotExist):
            Certificate.objects.get(id=certificate_id)
    
    def test_certificate_download_view(self):
        """Testa a view de download do certificado"""
        response = self.client.get(
            reverse('certificates:download', args=[self.certificate.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_certificate_expiring_soon_view(self):
        """Testa a view de certificados expirando em breve"""
        # Criar certificado que expira em breve
        expiring_certificate = Certificate.objects.create(
            versao='v3',
            num_serie='EXPIRING123',
            alg_assin='SHA256withRSA',
            alg_hash_assin='SHA256',
            emissor='Test CA',
            valid_ini=date.today(),
            valid_fim=date.today() + timedelta(days=15),  # Expira em 15 dias
            requerente='Expiring Company',
            chave_pub='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
            chave_pub_param='RSA 2048 bits',
            status=0,
            arquivo=b'expiring certificate content',
            usu_cad=self.user.email
        )
        
        response = self.client.get(reverse('certificates:expiring_soon'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Expiring Company')
        self.assertContains(response, 'EXPIRING123')


@pytest.mark.django_db
class CertificatePytestTest:
    """Testes usando pytest para Certificate"""
    
    def test_certificate_creation_with_pytest(self):
        """Teste de criação de certificado usando pytest"""
        user = User.objects.create_user(
            email='pytest@example.com',
            nome='Pytest User',
            password='testpass123'
        )
        
        certificate = Certificate.objects.create(
            versao='v3',
            num_serie='PYTEST123',
            alg_assin='SHA256withRSA',
            alg_hash_assin='SHA256',
            emissor='Pytest CA',
            valid_ini=date.today(),
            valid_fim=date.today() + timedelta(days=365),
            requerente='Pytest Company',
            chave_pub='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
            chave_pub_param='RSA 2048 bits',
            status=0,
            arquivo=b'pytest certificate content',
            usu_cad=user.email
        )
        
        assert certificate.versao == 'v3'
        assert certificate.num_serie == 'PYTEST123'
        assert certificate.requerente == 'Pytest Company'
        assert not certificate.is_expired
        assert certificate.days_until_expiry == 365
