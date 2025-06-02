from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import AlertRule, Alert, Metric, CostAlert
from apps.accounts.models import Account

User = get_user_model()


class MonitoringModelTest(TestCase):
    """Testes para os modelos de monitoramento"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            nome='Conta de Teste',
            account_id='123456789012',
            account_type='iam',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            default_region='us-east-1',
            status=0,
            is_validated=True,
            usu_cad=self.user.email
        )
    
    def test_create_alert_rule(self):
        """Testa criação de regra de alerta"""
        rule = AlertRule.objects.create(
            name='CPU High',
            description='Alerta de CPU alta',
            account=self.account,
            metric='cpu_utilization',
            operator='gt',
            threshold=80.0,
            severity='high',
            created_by=self.user.email
        )
        
        self.assertEqual(rule.name, 'CPU High')
        self.assertEqual(rule.account, self.account)
        self.assertEqual(rule.threshold, 80.0)
        self.assertEqual(rule.severity_badge_class, 'bg-danger')
    
    def test_create_alert(self):
        """Testa criação de alerta"""
        rule = AlertRule.objects.create(
            name='CPU High',
            account=self.account,
            metric='cpu_utilization',
            operator='gt',
            threshold=80.0,
            severity='critical',
            created_by=self.user.email
        )
        
        alert = Alert.objects.create(
            rule=rule,
            account=self.account,
            message='CPU utilization is 95%',
            current_value=95.0,
            threshold_value=80.0
        )
        
        self.assertEqual(alert.rule, rule)
        self.assertEqual(alert.status, 'open')
        self.assertEqual(alert.status_badge_class, 'bg-danger')
    
    def test_alert_acknowledge(self):
        """Testa reconhecimento de alerta"""
        rule = AlertRule.objects.create(
            name='CPU High',
            account=self.account,
            metric='cpu_utilization',
            operator='gt',
            threshold=80.0,
            created_by=self.user.email
        )
        
        alert = Alert.objects.create(
            rule=rule,
            account=self.account,
            message='CPU utilization is 95%',
            current_value=95.0,
            threshold_value=80.0
        )
        
        alert.acknowledge(self.user.email)
        
        self.assertEqual(alert.status, 'acknowledged')
        self.assertEqual(alert.acknowledged_by, self.user.email)
        self.assertIsNotNone(alert.acknowledged_at)
    
    def test_alert_resolve(self):
        """Testa resolução de alerta"""
        rule = AlertRule.objects.create(
            name='CPU High',
            account=self.account,
            metric='cpu_utilization',
            operator='gt',
            threshold=80.0,
            created_by=self.user.email
        )
        
        alert = Alert.objects.create(
            rule=rule,
            account=self.account,
            message='CPU utilization is 95%',
            current_value=95.0,
            threshold_value=80.0
        )
        
        alert.resolve(self.user.email)
        
        self.assertEqual(alert.status, 'resolved')
        self.assertEqual(alert.resolved_by, self.user.email)
        self.assertIsNotNone(alert.resolved_at)
    
    def test_create_metric(self):
        """Testa criação de métrica"""
        metric = Metric.objects.create(
            account=self.account,
            metric_name='CPUUtilization',
            namespace='AWS/EC2',
            value=75.5,
            unit='Percent',
            timestamp=timezone.now()
        )
        
        self.assertEqual(metric.account, self.account)
        self.assertEqual(metric.metric_name, 'CPUUtilization')
        self.assertEqual(metric.value, 75.5)
    
    def test_create_cost_alert(self):
        """Testa criação de alerta de custo"""
        cost_alert = CostAlert.objects.create(
            account=self.account,
            name='Budget Alert',
            budget_amount=1000.00,
            period='monthly',
            threshold_percentage=80,
            current_spend=850.00,
            created_by=self.user.email
        )
        
        self.assertEqual(cost_alert.account, self.account)
        self.assertEqual(cost_alert.usage_percentage, 85.0)
        self.assertTrue(cost_alert.is_over_threshold)


class MonitoringViewTest(TestCase):
    """Testes para as views de monitoramento"""
    
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
            account_id='123456789012',
            account_type='iam',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            default_region='us-east-1',
            status=0,
            is_validated=True,
            usu_cad=self.user.email
        )
    
    def test_monitoring_dashboard_view(self):
        """Testa a view do dashboard de monitoramento"""
        response = self.client.get(reverse('monitoring:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard de Monitoramento')
    
    def test_alert_list_view(self):
        """Testa a view de listagem de alertas"""
        response = self.client.get(reverse('monitoring:alert_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alertas')
    
    def test_alert_rule_list_view(self):
        """Testa a view de listagem de regras"""
        response = self.client.get(reverse('monitoring:alert_rule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Regras de Alerta')
    
    def test_alert_rule_create_view_get(self):
        """Testa a view de criação de regra (GET)"""
        response = self.client.get(reverse('monitoring:alert_rule_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Regra de Alerta')
    
    def test_alert_rule_create_view_post(self):
        """Testa a view de criação de regra (POST)"""
        data = {
            'name': 'CPU High Test',
            'description': 'Teste de CPU alta',
            'account': self.account.id,
            'metric': 'cpu_utilization',
            'operator': 'gt',
            'threshold': 80.0,
            'severity': 'high',
            'is_enabled': True,
            'notify_email': True,
            'notify_slack': False,
            'check_interval': 5,
            'cooldown_period': 30
        }
        
        response = self.client.post(reverse('monitoring:alert_rule_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect após criação
        
        # Verifica se a regra foi criada
        rule = AlertRule.objects.get(name='CPU High Test')
        self.assertEqual(rule.account, self.account)
        self.assertEqual(rule.threshold, 80.0)
    
    def test_metrics_view(self):
        """Testa a view de métricas"""
        response = self.client.get(reverse('monitoring:metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Métricas')
    
    def test_cost_alerts_list_view(self):
        """Testa a view de alertas de custo"""
        response = self.client.get(reverse('monitoring:cost_alerts_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alertas de Custo')
    
    def test_cost_alert_create_view_get(self):
        """Testa a view de criação de alerta de custo (GET)"""
        response = self.client.get(reverse('monitoring:cost_alert_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Novo Alerta de Custo')
    
    def test_alert_acknowledge_action(self):
        """Testa ação de reconhecer alerta"""
        rule = AlertRule.objects.create(
            name='CPU High',
            account=self.account,
            metric='cpu_utilization',
            operator='gt',
            threshold=80.0,
            created_by=self.user.email
        )
        
        alert = Alert.objects.create(
            rule=rule,
            account=self.account,
            message='CPU utilization is 95%',
            current_value=95.0,
            threshold_value=80.0
        )
        
        response = self.client.post(
            reverse('monitoring:alert_acknowledge', args=[alert.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verifica se o alerta foi reconhecido
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'acknowledged')
    
    def test_alert_resolve_action(self):
        """Testa ação de resolver alerta"""
        rule = AlertRule.objects.create(
            name='CPU High',
            account=self.account,
            metric='cpu_utilization',
            operator='gt',
            threshold=80.0,
            created_by=self.user.email
        )
        
        alert = Alert.objects.create(
            rule=rule,
            account=self.account,
            message='CPU utilization is 95%',
            current_value=95.0,
            threshold_value=80.0
        )
        
        response = self.client.post(
            reverse('monitoring:alert_resolve', args=[alert.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verifica se o alerta foi resolvido
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')
