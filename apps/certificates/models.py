from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    """
    Modelo de certificados conforme especificado no PRD
    """
    STATUS_CHOICES = [
        (0, 'Ativo'),
        (1, 'Inativo'),
        (2, 'Expirado'),
        (3, 'Revogado'),
        (4, 'Pendente'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    versao = models.CharField(max_length=255, verbose_name='Versão')
    num_serie = models.CharField(max_length=255, verbose_name='Número de Série')
    alg_assin = models.CharField(max_length=255, verbose_name='Algoritmo de Assinatura')
    alg_hash_assin = models.CharField(max_length=255, verbose_name='Algoritmo Hash de Assinatura')
    emissor = models.CharField(max_length=255, verbose_name='Emissor')
    valid_ini = models.DateField(verbose_name='Validade Inicial')
    valid_fim = models.DateField(verbose_name='Validade Final')
    requerente = models.CharField(max_length=255, verbose_name='Requerente')
    chave_pub = models.TextField(verbose_name='Chave Pública')
    chave_pub_param = models.TextField(verbose_name='Parâmetros da Chave Pública')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Status')
    arquivo = models.BinaryField(verbose_name='Arquivo do Certificado')
    data_cad = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    usu_cad = models.CharField(max_length=255, verbose_name='Usuário de Cadastro')
    data_atu = models.DateTimeField(null=True, blank=True, verbose_name='Data de Atualização')
    usu_atu = models.CharField(max_length=255, null=True, blank=True, verbose_name='Usuário de Atualização')
    
    class Meta:
        db_table = 'certificates'
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        
    def __str__(self):
        return f"{self.requerente} - {self.num_serie}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar ID único se não fornecido
            import uuid
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Verifica se o certificado está expirado"""
        from django.utils import timezone
        return self.valid_fim < timezone.now().date()
    
    @property
    def days_until_expiry(self):
        """Retorna quantos dias faltam para o certificado expirar"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.valid_fim > today:
            return (self.valid_fim - today).days
        return 0
