from django.db import models
from django.utils import timezone


class Account(models.Model):
    """
    Modelo de contas cloud conforme especificado no PRD
    """
    id = models.CharField(max_length=255, primary_key=True)
    nome = models.CharField(max_length=255, verbose_name='Nome da Conta')
    id_conta = models.CharField(max_length=255, verbose_name='ID da Conta')
    client = models.CharField(max_length=255, verbose_name='Client')
    secret = models.CharField(max_length=255, verbose_name='Secret')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'accounts'
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        
    def __str__(self):
        return f"{self.nome} ({self.id_conta})"
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar ID único se não fornecido
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
