#!/usr/bin/env python
"""
Script para criar dados de exemplo para o sistema de monitoramento
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fcm.settings')
django.setup()

from django.utils import timezone
from apps.accounts.models import Account
from monitoring.models import AlertRule, Alert, Metric, CostAlert

def create_sample_data():
    """Cria dados de exemplo para o sistema de monitoramento"""
    
    print("🔄 Criando dados de exemplo para o sistema de monitoramento...")
    
    # Buscar contas existentes
    accounts = Account.objects.all()
    if not accounts.exists():
        print("❌ Nenhuma conta AWS encontrada. Crie pelo menos uma conta primeiro.")
        return
    
    account = accounts.first()
    print(f"✅ Usando conta: {account.nome}")
    
    # 1. Criar regras de alerta
    print("\n📋 Criando regras de alerta...")
    
    rules_data = [
        {
            'name': 'CPU Alta - Produção',
            'description': 'Alerta quando CPU ultrapassa 80% em instâncias de produção',
            'metric': 'cpu_utilization',
            'operator': 'gt',
            'threshold': 80.0,
            'severity': 'critical',
            'check_interval': 5,
            'cooldown_period': 15,
            'notify_email': True,
            'notify_slack': False,
        },
        {
            'name': 'Memória Alta',
            'description': 'Alerta quando uso de memória ultrapassa 85%',
            'metric': 'memory_utilization',
            'operator': 'gt',
            'threshold': 85.0,
            'severity': 'high',
            'check_interval': 10,
            'cooldown_period': 30,
            'notify_email': True,
            'notify_slack': True,
            'slack_webhook': 'https://hooks.slack.com/services/example',
        },
        {
            'name': 'Disco Cheio',
            'description': 'Alerta quando uso de disco ultrapassa 90%',
            'metric': 'disk_utilization',
            'operator': 'gt',
            'threshold': 90.0,
            'severity': 'critical',
            'check_interval': 15,
            'cooldown_period': 60,
            'notify_email': True,
            'notify_slack': False,
        },
        {
            'name': 'Tráfego de Rede Baixo',
            'description': 'Alerta quando tráfego de rede está muito baixo',
            'metric': 'network_in',
            'operator': 'lt',
            'threshold': 1000.0,
            'severity': 'low',
            'check_interval': 30,
            'cooldown_period': 120,
            'notify_email': False,
            'notify_slack': True,
            'slack_webhook': 'https://hooks.slack.com/services/example',
        }
    ]
    
    created_rules = []
    for rule_data in rules_data:
        rule, created = AlertRule.objects.get_or_create(
            name=rule_data['name'],
            account=account,
            defaults=rule_data
        )
        if created:
            print(f"  ✅ Regra criada: {rule.name}")
        else:
            print(f"  ℹ️  Regra já existe: {rule.name}")
        created_rules.append(rule)
    
    # 2. Criar alertas
    print("\n🚨 Criando alertas...")
    
    now = timezone.now()
    alerts_data = [
        {
            'rule': created_rules[0],  # CPU Alta
            'message': 'CPU utilization is 85.2% on instance i-1234567890abcdef0',
            'current_value': 85.2,
            'threshold_value': 80.0,
            'status': 'open',
            'triggered_at': now - timedelta(minutes=30),
        },
        {
            'rule': created_rules[1],  # Memória Alta
            'message': 'Memory utilization is 87.5% on instance i-0987654321fedcba0',
            'current_value': 87.5,
            'threshold_value': 85.0,
            'status': 'acknowledged',
            'triggered_at': now - timedelta(hours=2),
            'acknowledged_at': now - timedelta(hours=1, minutes=30),
            'acknowledged_by': 'admin@example.com',
        },
        {
            'rule': created_rules[2],  # Disco Cheio
            'message': 'Disk space utilization is 92.1% on instance i-abcdef1234567890',
            'current_value': 92.1,
            'threshold_value': 90.0,
            'status': 'resolved',
            'triggered_at': now - timedelta(days=1),
            'acknowledged_at': now - timedelta(days=1) + timedelta(minutes=15),
            'acknowledged_by': 'admin@example.com',
            'resolved_at': now - timedelta(hours=6),
            'resolved_by': 'admin@example.com',
        },
        {
            'rule': created_rules[0],  # CPU Alta (outro alerta)
            'message': 'CPU utilization is 82.7% on instance i-fedcba0987654321',
            'current_value': 82.7,
            'threshold_value': 80.0,
            'status': 'open',
            'triggered_at': now - timedelta(minutes=10),
        }
    ]
    
    for alert_data in alerts_data:
        alert, created = Alert.objects.get_or_create(
            rule=alert_data['rule'],
            message=alert_data['message'],
            account=account,
            defaults=alert_data
        )
        if created:
            print(f"  ✅ Alerta criado: {alert.message[:50]}...")
        else:
            print(f"  ℹ️  Alerta já existe: {alert.message[:50]}...")
    
    # 3. Criar métricas
    print("\n📊 Criando métricas...")
    
    metrics_data = []
    base_time = now - timedelta(hours=24)
    
    # Gerar métricas para as últimas 24 horas (a cada hora)
    for i in range(24):
        timestamp = base_time + timedelta(hours=i)
        
        # CPU Utilization
        cpu_value = 70 + (i % 5) * 3 + (i % 3) * 2  # Varia entre 70-85%
        metrics_data.append({
            'metric_name': 'CPUUtilization',
            'namespace': 'AWS/EC2',
            'dimensions': '{"InstanceId": "i-1234567890abcdef0"}',
            'value': cpu_value,
            'unit': 'Percent',
            'timestamp': timestamp,
        })
        
        # Memory Utilization
        memory_value = 60 + (i % 7) * 4 + (i % 2) * 3  # Varia entre 60-85%
        metrics_data.append({
            'metric_name': 'MemoryUtilization',
            'namespace': 'CWAgent',
            'dimensions': '{"InstanceId": "i-0987654321fedcba0"}',
            'value': memory_value,
            'unit': 'Percent',
            'timestamp': timestamp,
        })
        
        # Network In
        network_value = 1000 + (i % 10) * 500  # Varia entre 1000-5500 bytes
        metrics_data.append({
            'metric_name': 'NetworkIn',
            'namespace': 'AWS/EC2',
            'dimensions': '{"InstanceId": "i-abcdef1234567890"}',
            'value': network_value,
            'unit': 'Bytes',
            'timestamp': timestamp,
        })
    
    for metric_data in metrics_data:
        metric, created = Metric.objects.get_or_create(
            account=account,
            metric_name=metric_data['metric_name'],
            timestamp=metric_data['timestamp'],
            defaults=metric_data
        )
        if created and len(metrics_data) <= 10:  # Só mostra os primeiros para não poluir
            print(f"  ✅ Métrica criada: {metric.metric_name} = {metric.value}")
    
    print(f"  ✅ Total de {len(metrics_data)} métricas criadas")
    
    # 4. Criar alertas de custo
    print("\n💰 Criando alertas de custo...")
    
    cost_alerts_data = [
        {
            'name': 'Budget Mensal - Produção',
            'budget_amount': Decimal('1000.00'),
            'current_spend': Decimal('750.50'),
            'period': 'monthly',
            'threshold_percentage': 75,
            'is_enabled': True,
        },
        {
            'name': 'Budget Semanal - Desenvolvimento',
            'budget_amount': Decimal('200.00'),
            'current_spend': Decimal('180.25'),
            'period': 'weekly',
            'threshold_percentage': 80,
            'is_enabled': True,
        },
        {
            'name': 'Budget Diário - Testes',
            'budget_amount': Decimal('50.00'),
            'current_spend': Decimal('35.75'),
            'period': 'daily',
            'threshold_percentage': 90,
            'is_enabled': True,
        }
    ]
    
    for cost_data in cost_alerts_data:
        cost_alert, created = CostAlert.objects.get_or_create(
            name=cost_data['name'],
            account=account,
            defaults=cost_data
        )
        if created:
            print(f"  ✅ Alerta de custo criado: {cost_alert.name}")
        else:
            print(f"  ℹ️  Alerta de custo já existe: {cost_alert.name}")
    
    print("\n🎉 Dados de exemplo criados com sucesso!")
    print("\n📋 Resumo:")
    print(f"  • {AlertRule.objects.count()} regras de alerta")
    print(f"  • {Alert.objects.count()} alertas")
    print(f"  • {Metric.objects.count()} métricas")
    print(f"  • {CostAlert.objects.count()} alertas de custo")
    print("\n🌐 Acesse o dashboard em: http://localhost:8000/monitoring/")

if __name__ == '__main__':
    create_sample_data() 