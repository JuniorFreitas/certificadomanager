from django.db import models
from django.utils import timezone


class Resource(models.Model):
    """
    Modelo de recursos cloud conforme especificado no PRD
    """
    RESOURCE_TYPE_CHOICES = [
        (0, 'S3'),
        (1, 'Load Balancer'),
        (2, 'CloudFront'),
        (3, 'API Gateway'),
        (4, 'EC2'),
        (5, 'RDS'),
        (6, 'Lambda'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    nome = models.CharField(max_length=255, verbose_name='Nome do Recurso')
    tipo = models.IntegerField(choices=RESOURCE_TYPE_CHOICES, verbose_name='Tipo do Recurso')
    url = models.URLField(verbose_name='URL do Recurso')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'resources'
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar ID único se não fornecido
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
