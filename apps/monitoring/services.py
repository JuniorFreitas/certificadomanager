import boto3
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Optional, Any
import logging

from .models import Metric, Alert, AlertRule
from apps.accounts.models import Account

logger = logging.getLogger(__name__)


class AWSCloudWatchService:
    """Serviço para integração com AWS CloudWatch"""
    
    def __init__(self, account: Account):
        self.account = account
        self.session = boto3.Session(
            aws_access_key_id=account.access_key,
            aws_secret_access_key=account.secret_key,
            region_name=account.region
        )
        self.cloudwatch = self.session.client('cloudwatch')
        self.ec2 = self.session.client('ec2')
        self.rds = self.session.client('rds')
        self.lambda_client = self.session.client('lambda')
        self.s3 = self.session.client('s3')
    
    def get_ec2_metrics(self, instance_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Coleta métricas de uma instância EC2"""
        metrics = []
        
        metric_queries = [
            {
                'name': 'CPUUtilization',
                'namespace': 'AWS/EC2',
                'statistic': 'Average',
                'unit': 'Percent'
            },
            {
                'name': 'NetworkIn',
                'namespace': 'AWS/EC2',
                'statistic': 'Sum',
                'unit': 'Bytes'
            },
            {
                'name': 'NetworkOut',
                'namespace': 'AWS/EC2',
                'statistic': 'Sum',
                'unit': 'Bytes'
            },
            {
                'name': 'DiskReadBytes',
                'namespace': 'AWS/EC2',
                'statistic': 'Sum',
                'unit': 'Bytes'
            },
            {
                'name': 'DiskWriteBytes',
                'namespace': 'AWS/EC2',
                'statistic': 'Sum',
                'unit': 'Bytes'
            }
        ]
        
        for metric_query in metric_queries:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace=metric_query['namespace'],
                    MetricName=metric_query['name'],
                    Dimensions=[
                        {
                            'Name': 'InstanceId',
                            'Value': instance_id
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5 minutos
                    Statistics=[metric_query['statistic']]
                )
                
                for datapoint in response['Datapoints']:
                    metrics.append({
                        'metric_name': metric_query['name'],
                        'namespace': metric_query['namespace'],
                        'value': datapoint[metric_query['statistic']],
                        'unit': metric_query['unit'],
                        'timestamp': datapoint['Timestamp'],
                        'dimensions': {'InstanceId': instance_id}
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao coletar métrica {metric_query['name']} para instância {instance_id}: {e}")
        
        return metrics
    
    def get_rds_metrics(self, db_instance_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Coleta métricas de uma instância RDS"""
        metrics = []
        
        metric_queries = [
            {
                'name': 'CPUUtilization',
                'namespace': 'AWS/RDS',
                'statistic': 'Average',
                'unit': 'Percent'
            },
            {
                'name': 'DatabaseConnections',
                'namespace': 'AWS/RDS',
                'statistic': 'Average',
                'unit': 'Count'
            },
            {
                'name': 'FreeableMemory',
                'namespace': 'AWS/RDS',
                'statistic': 'Average',
                'unit': 'Bytes'
            },
            {
                'name': 'FreeStorageSpace',
                'namespace': 'AWS/RDS',
                'statistic': 'Average',
                'unit': 'Bytes'
            }
        ]
        
        for metric_query in metric_queries:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace=metric_query['namespace'],
                    MetricName=metric_query['name'],
                    Dimensions=[
                        {
                            'Name': 'DBInstanceIdentifier',
                            'Value': db_instance_id
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,
                    Statistics=[metric_query['statistic']]
                )
                
                for datapoint in response['Datapoints']:
                    metrics.append({
                        'metric_name': metric_query['name'],
                        'namespace': metric_query['namespace'],
                        'value': datapoint[metric_query['statistic']],
                        'unit': metric_query['unit'],
                        'timestamp': datapoint['Timestamp'],
                        'dimensions': {'DBInstanceIdentifier': db_instance_id}
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao coletar métrica {metric_query['name']} para RDS {db_instance_id}: {e}")
        
        return metrics
    
    def get_lambda_metrics(self, function_name: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Coleta métricas de uma função Lambda"""
        metrics = []
        
        metric_queries = [
            {
                'name': 'Invocations',
                'namespace': 'AWS/Lambda',
                'statistic': 'Sum',
                'unit': 'Count'
            },
            {
                'name': 'Errors',
                'namespace': 'AWS/Lambda',
                'statistic': 'Sum',
                'unit': 'Count'
            },
            {
                'name': 'Duration',
                'namespace': 'AWS/Lambda',
                'statistic': 'Average',
                'unit': 'Milliseconds'
            },
            {
                'name': 'Throttles',
                'namespace': 'AWS/Lambda',
                'statistic': 'Sum',
                'unit': 'Count'
            }
        ]
        
        for metric_query in metric_queries:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace=metric_query['namespace'],
                    MetricName=metric_query['name'],
                    Dimensions=[
                        {
                            'Name': 'FunctionName',
                            'Value': function_name
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,
                    Statistics=[metric_query['statistic']]
                )
                
                for datapoint in response['Datapoints']:
                    metrics.append({
                        'metric_name': metric_query['name'],
                        'namespace': metric_query['namespace'],
                        'value': datapoint[metric_query['statistic']],
                        'unit': metric_query['unit'],
                        'timestamp': datapoint['Timestamp'],
                        'dimensions': {'FunctionName': function_name}
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao coletar métrica {metric_query['name']} para Lambda {function_name}: {e}")
        
        return metrics
    
    def get_s3_metrics(self, bucket_name: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Coleta métricas de um bucket S3"""
        metrics = []
        
        metric_queries = [
            {
                'name': 'BucketSizeBytes',
                'namespace': 'AWS/S3',
                'statistic': 'Average',
                'unit': 'Bytes',
                'storage_type': 'StandardStorage'
            },
            {
                'name': 'NumberOfObjects',
                'namespace': 'AWS/S3',
                'statistic': 'Average',
                'unit': 'Count',
                'storage_type': 'AllStorageTypes'
            }
        ]
        
        for metric_query in metric_queries:
            try:
                dimensions = [
                    {
                        'Name': 'BucketName',
                        'Value': bucket_name
                    }
                ]
                
                if 'storage_type' in metric_query:
                    dimensions.append({
                        'Name': 'StorageType',
                        'Value': metric_query['storage_type']
                    })
                
                response = self.cloudwatch.get_metric_statistics(
                    Namespace=metric_query['namespace'],
                    MetricName=metric_query['name'],
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,  # 1 dia para métricas S3
                    Statistics=[metric_query['statistic']]
                )
                
                for datapoint in response['Datapoints']:
                    metrics.append({
                        'metric_name': metric_query['name'],
                        'namespace': metric_query['namespace'],
                        'value': datapoint[metric_query['statistic']],
                        'unit': metric_query['unit'],
                        'timestamp': datapoint['Timestamp'],
                        'dimensions': {'BucketName': bucket_name}
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao coletar métrica {metric_query['name']} para S3 {bucket_name}: {e}")
        
        return metrics
    
    def list_ec2_instances(self) -> List[Dict]:
        """Lista todas as instâncias EC2"""
        try:
            response = self.ec2.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] in ['running', 'stopped']:
                        instances.append({
                            'instance_id': instance['InstanceId'],
                            'instance_type': instance['InstanceType'],
                            'state': instance['State']['Name'],
                            'name': self._get_instance_name(instance)
                        })
            
            return instances
        except Exception as e:
            logger.error(f"Erro ao listar instâncias EC2: {e}")
            return []
    
    def list_rds_instances(self) -> List[Dict]:
        """Lista todas as instâncias RDS"""
        try:
            response = self.rds.describe_db_instances()
            instances = []
            
            for db_instance in response['DBInstances']:
                instances.append({
                    'db_instance_id': db_instance['DBInstanceIdentifier'],
                    'db_instance_class': db_instance['DBInstanceClass'],
                    'engine': db_instance['Engine'],
                    'status': db_instance['DBInstanceStatus']
                })
            
            return instances
        except Exception as e:
            logger.error(f"Erro ao listar instâncias RDS: {e}")
            return []
    
    def list_lambda_functions(self) -> List[Dict]:
        """Lista todas as funções Lambda"""
        try:
            response = self.lambda_client.list_functions()
            functions = []
            
            for function in response['Functions']:
                functions.append({
                    'function_name': function['FunctionName'],
                    'runtime': function['Runtime'],
                    'memory_size': function['MemorySize'],
                    'timeout': function['Timeout']
                })
            
            return functions
        except Exception as e:
            logger.error(f"Erro ao listar funções Lambda: {e}")
            return []
    
    def list_s3_buckets(self) -> List[Dict]:
        """Lista todos os buckets S3"""
        try:
            response = self.s3.list_buckets()
            buckets = []
            
            for bucket in response['Buckets']:
                buckets.append({
                    'bucket_name': bucket['Name'],
                    'creation_date': bucket['CreationDate']
                })
            
            return buckets
        except Exception as e:
            logger.error(f"Erro ao listar buckets S3: {e}")
            return []
    
    def _get_instance_name(self, instance: Dict) -> str:
        """Extrai o nome da instância das tags"""
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    return tag['Value']
        return instance['InstanceId']


class MetricCollectionService:
    """Serviço para coleta e armazenamento de métricas"""
    
    @staticmethod
    def collect_metrics_for_account(account: Account) -> Dict[str, int]:
        """Coleta métricas para uma conta AWS"""
        aws_service = AWSCloudWatchService(account)
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=1)  # Última hora
        
        collected_metrics = {
            'ec2': 0,
            'rds': 0,
            'lambda': 0,
            's3': 0,
            'total': 0
        }
        
        try:
            # Coletar métricas EC2
            ec2_instances = aws_service.list_ec2_instances()
            for instance in ec2_instances:
                metrics = aws_service.get_ec2_metrics(
                    instance['instance_id'], 
                    start_time, 
                    end_time
                )
                MetricCollectionService._save_metrics(account, metrics)
                collected_metrics['ec2'] += len(metrics)
            
            # Coletar métricas RDS
            rds_instances = aws_service.list_rds_instances()
            for instance in rds_instances:
                metrics = aws_service.get_rds_metrics(
                    instance['db_instance_id'], 
                    start_time, 
                    end_time
                )
                MetricCollectionService._save_metrics(account, metrics)
                collected_metrics['rds'] += len(metrics)
            
            # Coletar métricas Lambda
            lambda_functions = aws_service.list_lambda_functions()
            for function in lambda_functions:
                metrics = aws_service.get_lambda_metrics(
                    function['function_name'], 
                    start_time, 
                    end_time
                )
                MetricCollectionService._save_metrics(account, metrics)
                collected_metrics['lambda'] += len(metrics)
            
            # Coletar métricas S3
            s3_buckets = aws_service.list_s3_buckets()
            for bucket in s3_buckets:
                metrics = aws_service.get_s3_metrics(
                    bucket['bucket_name'], 
                    start_time, 
                    end_time
                )
                MetricCollectionService._save_metrics(account, metrics)
                collected_metrics['s3'] += len(metrics)
            
            collected_metrics['total'] = sum([
                collected_metrics['ec2'],
                collected_metrics['rds'],
                collected_metrics['lambda'],
                collected_metrics['s3']
            ])
            
            logger.info(f"Coletadas {collected_metrics['total']} métricas para conta {account.nome}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas para conta {account.nome}: {e}")
        
        return collected_metrics
    
    @staticmethod
    def _save_metrics(account: Account, metrics: List[Dict]):
        """Salva métricas no banco de dados"""
        for metric_data in metrics:
            try:
                Metric.objects.get_or_create(
                    account=account,
                    metric_name=metric_data['metric_name'],
                    namespace=metric_data['namespace'],
                    timestamp=metric_data['timestamp'],
                    defaults={
                        'value': metric_data['value'],
                        'unit': metric_data['unit'],
                        'dimensions': metric_data['dimensions']
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao salvar métrica {metric_data['metric_name']}: {e}")


class AlertService:
    """Serviço para processamento de alertas"""
    
    @staticmethod
    def check_alert_rules():
        """Verifica todas as regras de alerta ativas"""
        active_rules = AlertRule.objects.filter(is_enabled=True)
        alerts_triggered = 0
        
        for rule in active_rules:
            try:
                if AlertService._should_trigger_alert(rule):
                    AlertService._trigger_alert(rule)
                    alerts_triggered += 1
            except Exception as e:
                logger.error(f"Erro ao verificar regra {rule.name}: {e}")
        
        logger.info(f"Verificadas {active_rules.count()} regras, {alerts_triggered} alertas disparados")
        return alerts_triggered
    
    @staticmethod
    def _should_trigger_alert(rule: AlertRule) -> bool:
        """Verifica se uma regra deve disparar um alerta"""
        # Verificar se já existe um alerta aberto para esta regra
        existing_alert = Alert.objects.filter(
            rule=rule,
            status='open'
        ).first()
        
        if existing_alert:
            # Verificar cooldown
            cooldown_time = existing_alert.triggered_at + timedelta(minutes=rule.cooldown_period)
            if timezone.now() < cooldown_time:
                return False
        
        # Buscar métricas recentes
        end_time = timezone.now()
        start_time = end_time - timedelta(minutes=rule.check_interval)
        
        recent_metrics = Metric.objects.filter(
            account=rule.account,
            metric_name=rule.metric,
            timestamp__gte=start_time,
            timestamp__lte=end_time
        ).order_by('-timestamp')
        
        if not recent_metrics.exists():
            return False
        
        # Verificar condição
        latest_metric = recent_metrics.first()
        current_value = latest_metric.value
        threshold = rule.threshold
        
        condition_met = False
        if rule.operator == 'gt':
            condition_met = current_value > threshold
        elif rule.operator == 'gte':
            condition_met = current_value >= threshold
        elif rule.operator == 'lt':
            condition_met = current_value < threshold
        elif rule.operator == 'lte':
            condition_met = current_value <= threshold
        elif rule.operator == 'eq':
            condition_met = current_value == threshold
        elif rule.operator == 'ne':
            condition_met = current_value != threshold
        
        return condition_met
    
    @staticmethod
    def _trigger_alert(rule: AlertRule):
        """Dispara um alerta"""
        # Buscar valor atual da métrica
        latest_metric = Metric.objects.filter(
            account=rule.account,
            metric_name=rule.metric
        ).order_by('-timestamp').first()
        
        if not latest_metric:
            return
        
        # Criar alerta
        alert = Alert.objects.create(
            rule=rule,
            account=rule.account,
            message=f"{rule.name}: {latest_metric.metric_name} = {latest_metric.value} {latest_metric.unit}",
            current_value=latest_metric.value,
            threshold_value=rule.threshold,
            status='open',
            metadata={
                'metric_name': latest_metric.metric_name,
                'namespace': latest_metric.namespace,
                'dimensions': latest_metric.dimensions,
                'timestamp': latest_metric.timestamp.isoformat()
            }
        )
        
        # Enviar notificações
        NotificationService.send_alert_notification(alert)
        
        logger.info(f"Alerta disparado: {alert.rule.name} - {alert.message}")


class NotificationService:
    """Serviço para envio de notificações"""
    
    @staticmethod
    def send_alert_notification(alert: Alert):
        """Envia notificação de alerta"""
        if alert.rule.notify_email:
            NotificationService._send_email_notification(alert)
        
        if alert.rule.notify_slack and alert.rule.slack_webhook:
            NotificationService._send_slack_notification(alert)
    
    @staticmethod
    def _send_email_notification(alert: Alert):
        """Envia notificação por email"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        try:
            subject = f"[FCM] Alerta: {alert.rule.name}"
            
            context = {
                'alert': alert,
                'rule': alert.rule,
                'account': alert.account
            }
            
            html_message = render_to_string('monitoring/email/alert_notification.html', context)
            plain_message = render_to_string('monitoring/email/alert_notification.txt', context)
            
            # Enviar para administradores (pode ser configurado)
            recipient_list = ['admin@finnet.com.br']  # Configurar conforme necessário
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email de alerta enviado para {recipient_list}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de alerta: {e}")
    
    @staticmethod
    def _send_slack_notification(alert: Alert):
        """Envia notificação para Slack"""
        import requests
        
        try:
            webhook_url = alert.rule.slack_webhook
            
            color_map = {
                'low': '#36a64f',      # Verde
                'medium': '#ff9500',   # Laranja
                'high': '#ff0000',     # Vermelho
                'critical': '#8b0000'  # Vermelho escuro
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.rule.severity, '#ff0000'),
                        "title": f"🚨 Alerta FCM: {alert.rule.name}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Conta AWS",
                                "value": alert.account.nome,
                                "short": True
                            },
                            {
                                "title": "Severidade",
                                "value": alert.rule.get_severity_display(),
                                "short": True
                            },
                            {
                                "title": "Valor Atual",
                                "value": f"{alert.current_value}",
                                "short": True
                            },
                            {
                                "title": "Limite",
                                "value": f"{alert.threshold_value}",
                                "short": True
                            }
                        ],
                        "footer": "FCM - Finnet Certificate Manager",
                        "ts": int(alert.triggered_at.timestamp())
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Notificação Slack enviada para alerta {alert.id}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Slack: {e}")


class CostMonitoringService:
    """Serviço para monitoramento de custos AWS"""
    
    def __init__(self, account: Account):
        self.account = account
        self.session = boto3.Session(
            aws_access_key_id=account.access_key,
            aws_secret_access_key=account.secret_key,
            region_name=account.region
        )
        self.cost_explorer = self.session.client('ce')
    
    def get_daily_costs(self, start_date: str, end_date: str) -> Dict:
        """Obtém custos diários"""
        try:
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            return response
        except Exception as e:
            logger.error(f"Erro ao obter custos diários: {e}")
            return {}
    
    def get_monthly_costs(self, start_date: str, end_date: str) -> Dict:
        """Obtém custos mensais"""
        try:
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost']
            )
            
            return response
        except Exception as e:
            logger.error(f"Erro ao obter custos mensais: {e}")
            return {} 