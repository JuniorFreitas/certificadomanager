from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager customizado para o modelo User"""
    
    def create_user(self, email, nome, password=None, **extra_fields):
        """Cria e salva um usuário comum"""
        if not email:
            raise ValueError('O email é obrigatório')
        if not nome:
            raise ValueError('O nome é obrigatório')
            
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nome, password=None, **extra_fields):
        """Cria e salva um superusuário"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 0)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
            
        return self.create_user(email, nome, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo customizado de usuário conforme especificado no PRD
    """
    STATUS_CHOICES = [
        (0, 'Ativo'),
        (1, 'Inativo'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    nome = models.CharField(max_length=255, verbose_name='Nome')
    email = models.EmailField(unique=True, verbose_name='Email')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Status')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro', blank=True)
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    # Sobrescrever campos do AbstractUser para usar nossos campos customizados
    username = None
    first_name = None
    last_name = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        
    def __str__(self):
        return f"{self.nome} ({self.email})"
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar ID único se não fornecido
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
