from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError
from cryptography.fernet import Fernet
from django.conf import settings
import uuid


class Account(models.Model):
    """
    Modelo de contas AWS conforme especificado no PRD
    """
    
    # Choices para status da conta
    STATUS_CHOICES = [
        (0, 'Ativa'),
        (1, 'Inativa'),
        (2, 'Suspensa'),
        (3, 'Em Validação'),
        (4, 'Erro de Conexão'),
    ]
    
    # Choices para tipo de conta
    ACCOUNT_TYPE_CHOICES = [
        ('root', 'Root Account'),
        ('iam', 'IAM User'),
        ('role', 'IAM Role'),
        ('federated', 'Federated User'),
    ]
    
    # Regiões AWS mais comuns
    AWS_REGIONS = [
        ('us-east-1', 'US East (N. Virginia)'),
        ('us-east-2', 'US East (Ohio)'),
        ('us-west-1', 'US West (N. California)'),
        ('us-west-2', 'US West (Oregon)'),
        ('eu-west-1', 'Europe (Ireland)'),
        ('eu-west-2', 'Europe (London)'),
        ('eu-west-3', 'Europe (Paris)'),
        ('eu-central-1', 'Europe (Frankfurt)'),
        ('ap-southeast-1', 'Asia Pacific (Singapore)'),
        ('ap-southeast-2', 'Asia Pacific (Sydney)'),
        ('ap-northeast-1', 'Asia Pacific (Tokyo)'),
        ('ap-south-1', 'Asia Pacific (Mumbai)'),
        ('sa-east-1', 'South America (São Paulo)'),
        ('ca-central-1', 'Canada (Central)'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    nome = models.CharField(max_length=255, verbose_name='Nome da Conta')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    
    # Informações da conta AWS
    account_id = models.CharField(
        max_length=12, 
        unique=True, 
        verbose_name='AWS Account ID',
        validators=[RegexValidator(r'^\d{12}$', 'Account ID deve ter 12 dígitos')]
    )
    account_type = models.CharField(
        max_length=20, 
        choices=ACCOUNT_TYPE_CHOICES, 
        default='iam',
        verbose_name='Tipo de Conta'
    )
    
    # Credenciais AWS (criptografadas)
    access_key_id = models.CharField(max_length=255, verbose_name='Access Key ID')
    secret_access_key = models.TextField(verbose_name='Secret Access Key')  # Será criptografado
    session_token = models.TextField(blank=True, null=True, verbose_name='Session Token')  # Para roles temporários
    
    # Configurações
    default_region = models.CharField(
        max_length=20, 
        choices=AWS_REGIONS, 
        default='us-east-1',
        verbose_name='Região Padrão'
    )
    enabled_regions = models.JSONField(
        default=list, 
        blank=True,
        verbose_name='Regiões Habilitadas',
        help_text='Lista de regiões onde a conta pode operar'
    )
    
    # Status e validação
    status = models.IntegerField(choices=STATUS_CHOICES, default=3, verbose_name='Status')
    is_validated = models.BooleanField(default=False, verbose_name='Validada')
    last_validation = models.DateTimeField(null=True, blank=True, verbose_name='Última Validação')
    validation_error = models.TextField(blank=True, null=True, verbose_name='Erro de Validação')
    
    # Informações da conta AWS (obtidas via API)
    account_alias = models.CharField(max_length=255, blank=True, null=True, verbose_name='Alias da Conta')
    account_email = models.EmailField(blank=True, null=True, verbose_name='Email da Conta')
    organization_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Organization ID')
    
    # Limites e cotas
    max_instances = models.IntegerField(default=20, verbose_name='Máximo de Instâncias')
    max_storage_gb = models.IntegerField(default=1000, verbose_name='Máximo de Storage (GB)')
    monthly_budget_usd = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Orçamento Mensal (USD)'
    )
    
    # Metadados
    tags = models.JSONField(default=dict, blank=True, verbose_name='Tags')
    
    # Auditoria
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'accounts'
        verbose_name = 'Conta AWS'
        verbose_name_plural = 'Contas AWS'
        ordering = ['nome']
        
    def __str__(self):
        return f"{self.nome} ({self.account_id})"
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        
        # Criptografar secret_access_key antes de salvar
        if self.secret_access_key and not self.secret_access_key.startswith('gAAAAAB'):
            self.secret_access_key = self._encrypt_secret(self.secret_access_key)
        
        super().save(*args, **kwargs)
    
    def _encrypt_secret(self, secret):
        """Criptografa o secret access key"""
        try:
            # Usar uma chave de criptografia do settings ou gerar uma
            key = getattr(settings, 'ENCRYPTION_KEY', Fernet.generate_key())
            f = Fernet(key)
            return f.encrypt(secret.encode()).decode()
        except Exception:
            # Fallback: retornar o secret sem criptografia (não recomendado para produção)
            return secret
    
    def _decrypt_secret(self, encrypted_secret):
        """Descriptografa o secret access key"""
        try:
            if not encrypted_secret.startswith('gAAAAAB'):
                return encrypted_secret  # Não está criptografado
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key:
                return encrypted_secret
            
            f = Fernet(key)
            return f.decrypt(encrypted_secret.encode()).decode()
        except Exception:
            return encrypted_secret
    
    @property
    def decrypted_secret(self):
        """Retorna o secret descriptografado"""
        return self._decrypt_secret(self.secret_access_key)
    
    @property
    def status_display(self):
        """Retorna o display do status"""
        return dict(self.STATUS_CHOICES)[self.status]
    
    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        badge_classes = {
            0: 'bg-success',    # Ativa
            1: 'bg-secondary',  # Inativa
            2: 'bg-warning',    # Suspensa
            3: 'bg-info',       # Em Validação
            4: 'bg-danger',     # Erro de Conexão
        }
        return badge_classes.get(self.status, 'bg-secondary')
    
    @property
    def is_active(self):
        """Verifica se a conta está ativa"""
        return self.status == 0
    
    def get_boto3_session(self, region_name=None):
        """Cria uma sessão boto3 com as credenciais da conta"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.decrypted_secret,
                aws_session_token=self.session_token if self.session_token else None,
                region_name=region_name or self.default_region
            )
            return session
        except Exception as e:
            raise ValidationError(f"Erro ao criar sessão AWS: {str(e)}")
    
    def get_boto3_client(self, service_name, region_name=None):
        """Cria um cliente boto3 para um serviço específico"""
        session = self.get_boto3_session(region_name)
        return session.client(service_name)
    
    def validate_credentials(self):
        """Valida as credenciais AWS"""
        try:
            # Tentar obter informações da conta usando STS
            sts_client = self.get_boto3_client('sts')
            response = sts_client.get_caller_identity()
            
            # Atualizar informações da conta
            self.account_id = response.get('Account', self.account_id)
            self.is_validated = True
            self.last_validation = timezone.now()
            self.validation_error = None
            self.status = 0  # Ativa
            
            # Tentar obter alias da conta
            try:
                iam_client = self.get_boto3_client('iam')
                aliases = iam_client.list_account_aliases()
                if aliases['AccountAliases']:
                    self.account_alias = aliases['AccountAliases'][0]
            except ClientError:
                pass  # Pode não ter permissão para listar aliases
            
            return True, "Credenciais validadas com sucesso"
            
        except NoCredentialsError:
            self.is_validated = False
            self.status = 4
            self.validation_error = "Credenciais não encontradas"
            return False, "Credenciais não encontradas"
            
        except ClientError as e:
            self.is_validated = False
            self.status = 4
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.validation_error = f"{error_code}: {error_message}"
            return False, f"Erro AWS: {error_message}"
            
        except Exception as e:
            self.is_validated = False
            self.status = 4
            self.validation_error = str(e)
            return False, f"Erro inesperado: {str(e)}"
    
    def get_account_info(self):
        """Obtém informações detalhadas da conta AWS"""
        if not self.is_validated:
            return None
        
        try:
            info = {}
            
            # Informações básicas via STS
            sts_client = self.get_boto3_client('sts')
            caller_identity = sts_client.get_caller_identity()
            info['account_id'] = caller_identity.get('Account')
            info['user_id'] = caller_identity.get('UserId')
            info['arn'] = caller_identity.get('Arn')
            
            # Informações de billing (se disponível)
            try:
                billing_client = self.get_boto3_client('ce', 'us-east-1')  # Cost Explorer só funciona em us-east-1
                # Aqui você pode adicionar chamadas para obter informações de custo
            except ClientError:
                pass  # Pode não ter permissão para billing
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_available_services(self):
        """Lista os serviços AWS disponíveis para esta conta"""
        if not self.is_validated:
            return []
        
        # Lista básica de serviços comuns
        common_services = [
            'ec2', 's3', 'rds', 'lambda', 'iam', 'cloudformation',
            'cloudwatch', 'sns', 'sqs', 'dynamodb', 'elasticache',
            'elbv2', 'route53', 'acm', 'secretsmanager'
        ]
        
        available_services = []
        
        for service in common_services:
            try:
                client = self.get_boto3_client(service)
                # Fazer uma chamada simples para verificar se o serviço está disponível
                if service == 'ec2':
                    client.describe_regions()
                elif service == 's3':
                    client.list_buckets()
                elif service == 'iam':
                    client.get_user()
                # Adicionar mais verificações conforme necessário
                
                available_services.append(service)
            except ClientError:
                continue  # Serviço não disponível ou sem permissão
            except Exception:
                continue
        
        return available_services
    
    def test_connection(self):
        """Testa a conexão com a AWS"""
        try:
            success, message = self.validate_credentials()
            if success:
                # Salvar as informações atualizadas
                self.save()
            return success, message
        except Exception as e:
            return False, f"Erro ao testar conexão: {str(e)}"
    
    def get_resource_summary(self):
        """Obtém um resumo dos recursos da conta"""
        if not self.is_validated:
            return {}
        
        summary = {}
        
        try:
            # EC2 Instances
            ec2_client = self.get_boto3_client('ec2')
            instances = ec2_client.describe_instances()
            instance_count = sum(len(reservation['Instances']) for reservation in instances['Reservations'])
            summary['ec2_instances'] = instance_count
            
            # S3 Buckets
            s3_client = self.get_boto3_client('s3')
            buckets = s3_client.list_buckets()
            summary['s3_buckets'] = len(buckets['Buckets'])
            
            # RDS Instances
            try:
                rds_client = self.get_boto3_client('rds')
                db_instances = rds_client.describe_db_instances()
                summary['rds_instances'] = len(db_instances['DBInstances'])
            except ClientError:
                summary['rds_instances'] = 0
            
            # Lambda Functions
            try:
                lambda_client = self.get_boto3_client('lambda')
                functions = lambda_client.list_functions()
                summary['lambda_functions'] = len(functions['Functions'])
            except ClientError:
                summary['lambda_functions'] = 0
                
        except Exception as e:
            summary['error'] = str(e)
        
        return summary


class AccountRegion(models.Model):
    """
    Modelo para gerenciar regiões específicas de uma conta
    """
    id = models.CharField(max_length=255, primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='regions')
    region_code = models.CharField(max_length=20, choices=Account.AWS_REGIONS, verbose_name='Região')
    is_enabled = models.BooleanField(default=True, verbose_name='Habilitada')
    is_default = models.BooleanField(default=False, verbose_name='Região Padrão')
    
    # Auditoria
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    
    class Meta:
        db_table = 'account_regions'
        verbose_name = 'Região da Conta'
        verbose_name_plural = 'Regiões das Contas'
        unique_together = ['account', 'region_code']
    
    def __str__(self):
        return f"{self.account.nome} - {self.get_region_code_display()}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)


class AccountService(models.Model):
    """
    Modelo para rastrear serviços AWS habilitados por conta
    """
    id = models.CharField(max_length=255, primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=50, verbose_name='Nome do Serviço')
    is_enabled = models.BooleanField(default=True, verbose_name='Habilitado')
    last_check = models.DateTimeField(null=True, blank=True, verbose_name='Última Verificação')
    
    # Auditoria
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    
    class Meta:
        db_table = 'account_services'
        verbose_name = 'Serviço da Conta'
        verbose_name_plural = 'Serviços das Contas'
        unique_together = ['account', 'service_name']
    
    def __str__(self):
        return f"{self.account.nome} - {self.service_name}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
