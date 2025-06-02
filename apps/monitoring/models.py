import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.accounts.models import Account
import json

User = get_user_model()


class AlertRule(models.Model):
    """Regras de alerta para monitoramento"""
    
    SEVERITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    OPERATOR_CHOICES = [
        ('gt', 'Maior que'),
        ('gte', 'Maior ou igual'),
        ('lt', 'Menor que'),
        ('lte', 'Menor ou igual'),
        ('eq', 'Igual'),
        ('ne', 'Diferente'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nome', max_length=255)
    description = models.TextField('Descrição', blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Conta')
    metric = models.CharField('Métrica', max_length=255)
    operator = models.CharField('Operador', max_length=10, choices=OPERATOR_CHOICES)
    threshold = models.FloatField('Limite')
    severity = models.CharField('Severidade', max_length=20, choices=SEVERITY_CHOICES)
    is_enabled = models.BooleanField('Ativo', default=True)
    check_interval = models.IntegerField('Intervalo de Verificação (min)', default=5)
    cooldown_period = models.IntegerField('Período de Cooldown (min)', default=15)
    notify_email = models.BooleanField('Notificar por Email', default=True)
    notify_slack = models.BooleanField('Notificar por Slack', default=False)
    slack_webhook = models.URLField('Webhook Slack', blank=True)
    created_by = models.CharField('Criado por', max_length=255)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Regra de Alerta'
        verbose_name_plural = 'Regras de Alerta'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def severity_badge_class(self):
        """Classe CSS para badge de severidade"""
        return {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger',
            'critical': 'bg-dark'
        }.get(self.severity, 'bg-secondary')


class Alert(models.Model):
    """Alertas disparados"""
    
    STATUS_CHOICES = [
        ('open', 'Aberto'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
        ('suppressed', 'Suprimido'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name='Regra')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Conta')
    message = models.TextField('Mensagem')
    current_value = models.FloatField('Valor Atual')
    threshold_value = models.FloatField('Valor Limite')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='open')
    triggered_at = models.DateTimeField('Disparado em', auto_now_add=True)
    acknowledged_at = models.DateTimeField('Reconhecido em', null=True, blank=True)
    acknowledged_by = models.CharField('Reconhecido por', max_length=255, blank=True)
    resolved_at = models.DateTimeField('Resolvido em', null=True, blank=True)
    resolved_by = models.CharField('Resolvido por', max_length=255, blank=True)
    metadata = models.JSONField('Metadados', default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.rule.name} - {self.get_status_display()}"
    
    @property
    def status_badge_class(self):
        """Classe CSS para badge de status"""
        return {
            'open': 'bg-danger',
            'acknowledged': 'bg-warning',
            'resolved': 'bg-success',
            'suppressed': 'bg-secondary'
        }.get(self.status, 'bg-secondary')
    
    @property
    def severity_badge_class(self):
        """Classe CSS para badge de severidade"""
        return self.rule.severity_badge_class
    
    def acknowledge(self, user_email):
        """Reconhecer alerta"""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user_email
        self.save()
    
    def resolve(self, user_email):
        """Resolver alerta"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolved_by = user_email
        self.save()


class Metric(models.Model):
    """Métricas coletadas"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Conta')
    metric_name = models.CharField('Nome da Métrica', max_length=255)
    namespace = models.CharField('Namespace', max_length=255)
    value = models.FloatField('Valor')
    unit = models.CharField('Unidade', max_length=50, blank=True)
    timestamp = models.DateTimeField('Timestamp')
    dimensions = models.JSONField('Dimensões', default=dict, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Métrica'
        verbose_name_plural = 'Métricas'
        ordering = ['-timestamp']
        unique_together = ['account', 'metric_name', 'namespace', 'timestamp']
    
    def __str__(self):
        return f"{self.metric_name} - {self.value} {self.unit}"


class MonitoringDashboard(models.Model):
    """Dashboards personalizados"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nome', max_length=255)
    description = models.TextField('Descrição', blank=True)
    config = models.JSONField('Configuração', default=dict)
    is_default = models.BooleanField('Dashboard Padrão', default=False)
    created_by = models.CharField('Criado por', max_length=255)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class CostAlert(models.Model):
    """Alertas de custo"""
    
    PERIOD_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nome', max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Conta')
    threshold = models.DecimalField('Limite (USD)', max_digits=10, decimal_places=2, default=100.00)
    period = models.CharField('Período', max_length=20, choices=PERIOD_CHOICES)
    is_enabled = models.BooleanField('Ativo', default=True)
    notify_email = models.BooleanField('Notificar por Email', default=True)
    created_by = models.CharField('Criado por', max_length=255)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Alerta de Custo'
        verbose_name_plural = 'Alertas de Custo'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
