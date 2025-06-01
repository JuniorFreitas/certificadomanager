from django.db import models
from django.utils import timezone
from apps.users.models import User


class Role(models.Model):
    """
    Modelo de roles/funções do sistema
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('user', 'Usuário'),
        ('viewer', 'Visualizador'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name='Nome do Role')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()
    
    def save(self, *args, **kwargs):
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    @property
    def badge_class(self):
        """Retorna a classe CSS para o badge do role"""
        badge_classes = {
            'admin': 'bg-danger',
            'manager': 'bg-warning',
            'user': 'bg-primary',
            'viewer': 'bg-secondary',
        }
        return badge_classes.get(self.name, 'bg-secondary')


class Permission(models.Model):
    """
    Modelo de permissões dos usuários conforme especificado no PRD
    """
    PERMISSION_CHOICES = [
        ('users_create', 'Criar Usuários'),
        ('users_edit', 'Editar Usuários'),
        ('users_delete', 'Excluir Usuários'),
        ('users_view', 'Visualizar Usuários'),
        ('certificates_create', 'Criar Certificados'),
        ('certificates_edit', 'Editar Certificados'),
        ('certificates_delete', 'Excluir Certificados'),
        ('certificates_view', 'Visualizar Certificados'),
        ('accounts_create', 'Criar Contas'),
        ('accounts_edit', 'Editar Contas'),
        ('accounts_delete', 'Excluir Contas'),
        ('accounts_view', 'Visualizar Contas'),
        ('resources_create', 'Criar Recursos'),
        ('resources_edit', 'Editar Recursos'),
        ('resources_delete', 'Excluir Recursos'),
        ('resources_view', 'Visualizar Recursos'),
        ('permissions_create', 'Criar Permissões'),
        ('permissions_edit', 'Editar Permissões'),
        ('permissions_delete', 'Excluir Permissões'),
        ('permissions_view', 'Visualizar Permissões'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    permission_type = models.CharField(max_length=50, choices=PERMISSION_CHOICES, verbose_name='Tipo de Permissão')
    granted = models.BooleanField(default=True, verbose_name='Concedida')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'
        unique_together = ['user', 'permission_type']
        ordering = ['user__nome', 'permission_type']
        
    def __str__(self):
        return f"{self.user.nome} - {self.get_permission_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar ID único se não fornecido
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    @property
    def module_name(self):
        """Retorna o nome do módulo da permissão"""
        return self.permission_type.split('_')[0].title()
    
    @property
    def action_name(self):
        """Retorna o nome da ação da permissão"""
        return self.permission_type.split('_')[1].title()
    
    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        return 'bg-success' if self.granted else 'bg-danger'


class UserRole(models.Model):
    """
    Modelo de associação entre usuários e roles
    """
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Role')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = 'Role do Usuário'
        verbose_name_plural = 'Roles dos Usuários'
        unique_together = ['user', 'role']
        ordering = ['user__nome', 'role__name']
    
    def __str__(self):
        return f"{self.user.nome} - {self.role.get_name_display()}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
