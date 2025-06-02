from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta, datetime
import json
import boto3
from botocore.exceptions import ClientError

from .models import AlertRule, Alert, Metric, MonitoringDashboard, CostAlert
from apps.accounts.models import Account
from .forms import AlertRuleForm, CostAlertForm, MonitoringDashboardForm


@login_required
def monitoring_dashboard(request):
    """Dashboard principal de monitoramento"""
    
    # Estatísticas gerais
    stats = {
        'total_alerts': Alert.objects.filter(status='open').count(),
        'critical_alerts': Alert.objects.filter(
            status='open', 
            rule__severity='critical'
        ).count(),
        'total_rules': AlertRule.objects.filter(is_enabled=True).count(),
        'monitored_accounts': Account.objects.filter(
            alertrule__is_enabled=True
        ).distinct().count(),
    }
    
    # Alertas recentes
    recent_alerts = Alert.objects.select_related('rule', 'account').filter(
        status='open'
    ).order_by('-triggered_at')[:10]
    
    # Alertas por severidade
    alerts_by_severity = Alert.objects.filter(status='open').values(
        'rule__severity'
    ).annotate(count=Count('id')).order_by('rule__severity')
    
    # Métricas das últimas 24 horas
    last_24h = timezone.now() - timedelta(hours=24)
    recent_metrics = Metric.objects.filter(
        timestamp__gte=last_24h
    ).values('metric_name').annotate(
        avg_value=Avg('value'),
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Contas com mais alertas
    accounts_with_alerts = Alert.objects.filter(
        status='open'
    ).values('account__nome').annotate(
        alert_count=Count('id')
    ).order_by('-alert_count')[:5]
    
    # Custos por conta (simulado)
    cost_alerts = CostAlert.objects.filter(
        is_enabled=True
    ).select_related('account')[:5]
    
    context = {
        'title': 'Dashboard de Monitoramento',
        'stats': stats,
        'recent_alerts': recent_alerts,
        'alerts_by_severity': alerts_by_severity,
        'recent_metrics': recent_metrics,
        'accounts_with_alerts': accounts_with_alerts,
        'cost_alerts': cost_alerts,
    }
    
    return render(request, 'monitoring/dashboard.html', context)


@login_required
def alert_list(request):
    """Lista de alertas"""
    
    # Filtros
    status_filter = request.GET.get('status', '')
    severity_filter = request.GET.get('severity', '')
    account_filter = request.GET.get('account', '')
    
    alerts = Alert.objects.select_related('rule', 'account').all()
    
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    if severity_filter:
        alerts = alerts.filter(rule__severity=severity_filter)
    
    if account_filter:
        alerts = alerts.filter(account_id=account_filter)
    
    # Paginação
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas para filtros
    stats = {
        'total': Alert.objects.count(),
        'open': Alert.objects.filter(status='open').count(),
        'acknowledged': Alert.objects.filter(status='acknowledged').count(),
        'resolved': Alert.objects.filter(status='resolved').count(),
    }
    
    # Contas para filtro
    accounts = Account.objects.filter(
        alert__isnull=False
    ).distinct().order_by('nome')
    
    context = {
        'title': 'Alertas',
        'page_obj': page_obj,
        'stats': stats,
        'accounts': accounts,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'account_filter': account_filter,
    }
    
    return render(request, 'monitoring/alert_list.html', context)


@login_required
def alert_detail(request, alert_id):
    """Detalhes do alerta"""
    alert = get_object_or_404(Alert, id=alert_id)
    
    context = {
        'title': f'Alerta: {alert.rule.name}',
        'alert': alert,
    }
    
    return render(request, 'monitoring/alert_detail.html', context)


@login_required
def alert_acknowledge(request, alert_id):
    """Reconhecer alerta"""
    alert = get_object_or_404(Alert, id=alert_id)
    
    if request.method == 'POST':
        alert.acknowledge(request.user.email)
        messages.success(request, f'Alerta "{alert.rule.name}" reconhecido com sucesso.')
        return redirect('monitoring:alert_detail', alert_id=alert.id)
    
    return redirect('monitoring:alert_detail', alert_id=alert.id)


@login_required
def alert_resolve(request, alert_id):
    """Resolver alerta"""
    alert = get_object_or_404(Alert, id=alert_id)
    
    if request.method == 'POST':
        alert.resolve(request.user.email)
        messages.success(request, f'Alerta "{alert.rule.name}" resolvido com sucesso.')
        return redirect('monitoring:alert_detail', alert_id=alert.id)
    
    return redirect('monitoring:alert_detail', alert_id=alert.id)


@login_required
def alert_rule_list(request):
    """Lista de regras de alerta"""
    
    rules = AlertRule.objects.select_related('account').all()
    
    # Filtros
    account_filter = request.GET.get('account', '')
    if account_filter:
        rules = rules.filter(account_id=account_filter)
    
    # Paginação
    paginator = Paginator(rules, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': AlertRule.objects.count(),
        'enabled': AlertRule.objects.filter(is_enabled=True).count(),
        'disabled': AlertRule.objects.filter(is_enabled=False).count(),
    }
    
    # Contas para filtro
    accounts = Account.objects.all().order_by('nome')
    
    context = {
        'title': 'Regras de Alerta',
        'page_obj': page_obj,
        'stats': stats,
        'accounts': accounts,
        'account_filter': account_filter,
    }
    
    return render(request, 'monitoring/alert_rule_list.html', context)


@login_required
def alert_rule_create(request):
    """Criar regra de alerta"""
    
    if request.method == 'POST':
        form = AlertRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.created_by = request.user.email
            rule.save()
            messages.success(request, f'Regra de alerta "{rule.name}" criada com sucesso.')
            return redirect('monitoring:alert_rule_list')
    else:
        form = AlertRuleForm()
    
    context = {
        'title': 'Nova Regra de Alerta',
        'form': form,
    }
    
    return render(request, 'monitoring/alert_rule_form.html', context)


@login_required
def alert_rule_edit(request, rule_id):
    """Editar regra de alerta"""
    rule = get_object_or_404(AlertRule, id=rule_id)
    
    if request.method == 'POST':
        form = AlertRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, f'Regra de alerta "{rule.name}" atualizada com sucesso.')
            return redirect('monitoring:alert_rule_list')
    else:
        form = AlertRuleForm(instance=rule)
    
    context = {
        'title': f'Editar Regra: {rule.name}',
        'form': form,
        'rule': rule,
    }
    
    return render(request, 'monitoring/alert_rule_form.html', context)


@login_required
def alert_rule_delete(request, rule_id):
    """Excluir regra de alerta"""
    rule = get_object_or_404(AlertRule, id=rule_id)
    
    if request.method == 'POST':
        rule_name = rule.name
        rule.delete()
        messages.success(request, f'Regra de alerta "{rule_name}" excluída com sucesso.')
        return redirect('monitoring:alert_rule_list')
    
    context = {
        'title': f'Excluir Regra: {rule.name}',
        'rule': rule,
    }
    
    return render(request, 'monitoring/alert_rule_delete.html', context)


@login_required
def metrics_view(request):
    """Visualização de métricas"""
    
    # Filtros
    account_filter = request.GET.get('account', '')
    metric_filter = request.GET.get('metric', '')
    period = request.GET.get('period', '24h')
    
    # Calcular período
    if period == '1h':
        start_time = timezone.now() - timedelta(hours=1)
    elif period == '6h':
        start_time = timezone.now() - timedelta(hours=6)
    elif period == '24h':
        start_time = timezone.now() - timedelta(hours=24)
    elif period == '7d':
        start_time = timezone.now() - timedelta(days=7)
    else:
        start_time = timezone.now() - timedelta(hours=24)
    
    metrics = Metric.objects.filter(timestamp__gte=start_time)
    
    if account_filter:
        metrics = metrics.filter(account_id=account_filter)
    
    if metric_filter:
        metrics = metrics.filter(metric_name=metric_filter)
    
    # Agrupar métricas por nome
    metrics_by_name = {}
    for metric in metrics.order_by('timestamp'):
        if metric.metric_name not in metrics_by_name:
            metrics_by_name[metric.metric_name] = []
        metrics_by_name[metric.metric_name].append({
            'timestamp': metric.timestamp.isoformat(),
            'value': metric.value,
            'account': metric.account.nome,
        })
    
    # Contas e métricas para filtros
    accounts = Account.objects.all().order_by('nome')
    available_metrics = Metric.objects.values_list(
        'metric_name', flat=True
    ).distinct().order_by('metric_name')
    
    context = {
        'title': 'Métricas',
        'metrics_data': json.dumps(metrics_by_name),
        'accounts': accounts,
        'available_metrics': available_metrics,
        'account_filter': account_filter,
        'metric_filter': metric_filter,
        'period': period,
    }
    
    return render(request, 'monitoring/metrics.html', context)


@login_required
def cost_alerts_list(request):
    """Lista de alertas de custo"""
    
    cost_alerts = CostAlert.objects.select_related('account').all()
    
    # Paginação
    paginator = Paginator(cost_alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Alertas de Custo',
        'page_obj': page_obj,
    }
    
    return render(request, 'monitoring/cost_alert_list.html', context)


@login_required
def cost_alert_create(request):
    """Criar alerta de custo"""
    
    if request.method == 'POST':
        form = CostAlertForm(request.POST)
        if form.is_valid():
            cost_alert = form.save(commit=False)
            cost_alert.created_by = request.user.email
            cost_alert.save()
            messages.success(request, f'Alerta de custo "{cost_alert.name}" criado com sucesso.')
            return redirect('monitoring:cost_alerts_list')
    else:
        form = CostAlertForm()
    
    context = {
        'title': 'Novo Alerta de Custo',
        'form': form,
    }
    
    return render(request, 'monitoring/cost_alert_form.html', context)


@login_required
def api_collect_metrics(request):
    """API para coletar métricas do CloudWatch"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        account_id = data.get('account_id')
        
        if not account_id:
            return JsonResponse({'error': 'Account ID é obrigatório'}, status=400)
        
        account = get_object_or_404(Account, id=account_id)
        
        if not account.is_validated:
            return JsonResponse({'error': 'Conta não validada'}, status=400)
        
        # Coletar métricas do CloudWatch
        collected_metrics = _collect_cloudwatch_metrics(account)
        
        return JsonResponse({
            'success': True,
            'message': f'{len(collected_metrics)} métricas coletadas com sucesso',
            'metrics': collected_metrics
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _collect_cloudwatch_metrics(account):
    """Coleta métricas do CloudWatch"""
    collected_metrics = []
    
    try:
        # Cliente CloudWatch
        cloudwatch = account.get_boto3_client('cloudwatch')
        
        # Métricas EC2
        ec2_metrics = [
            'CPUUtilization',
            'NetworkIn',
            'NetworkOut',
            'DiskReadOps',
            'DiskWriteOps'
        ]
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        for metric_name in ec2_metrics:
            try:
                response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric_name,
                    Dimensions=[],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5 minutos
                    Statistics=['Average']
                )
                
                for datapoint in response['Datapoints']:
                    metric = Metric.objects.create(
                        account=account,
                        metric_name=metric_name,
                        namespace='AWS/EC2',
                        value=datapoint['Average'],
                        unit=datapoint.get('Unit', ''),
                        timestamp=datapoint['Timestamp']
                    )
                    collected_metrics.append({
                        'name': metric_name,
                        'value': datapoint['Average'],
                        'timestamp': datapoint['Timestamp'].isoformat()
                    })
                    
            except ClientError as e:
                continue
                
    except Exception as e:
        pass
    
    return collected_metrics


@login_required
def advanced_dashboard(request):
    """Dashboard avançado com gráficos interativos"""
    
    # Dados para gráficos de métricas ao longo do tempo
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=24)
    
    # Métricas de CPU ao longo do tempo
    cpu_metrics = Metric.objects.filter(
        metric_name='CPUUtilization',
        timestamp__gte=start_time,
        timestamp__lte=end_time
    ).values('timestamp', 'value', 'account__nome').order_by('timestamp')
    
    # Métricas de memória
    memory_metrics = Metric.objects.filter(
        metric_name='MemoryUtilization',
        timestamp__gte=start_time,
        timestamp__lte=end_time
    ).values('timestamp', 'value', 'account__nome').order_by('timestamp')
    
    # Alertas por severidade
    alert_severity_data = Alert.objects.filter(
        triggered_at__gte=start_time
    ).values('rule__severity').annotate(count=Count('id'))
    
    # Alertas ao longo do tempo (últimos 7 dias)
    week_start = end_time - timedelta(days=7)
    daily_alerts = Alert.objects.filter(
        triggered_at__gte=week_start
    ).extra(
        select={'day': 'date(triggered_at)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Métricas por conta AWS
    account_metrics = Metric.objects.filter(
        timestamp__gte=start_time
    ).values('account__nome').annotate(
        avg_cpu=Avg('value', filter=Q(metric_name='CPUUtilization')),
        avg_memory=Avg('value', filter=Q(metric_name='MemoryUtilization')),
        total_metrics=Count('id')
    )
    
    # Top 5 recursos com mais alertas
    top_alert_resources = Alert.objects.filter(
        triggered_at__gte=week_start
    ).values('account__nome').annotate(
        alert_count=Count('id')
    ).order_by('-alert_count')[:5]
    
    # Distribuição de tipos de métricas
    metric_types = Metric.objects.filter(
        timestamp__gte=start_time
    ).values('metric_name').annotate(count=Count('id')).order_by('-count')
    
    # Status dos alertas
    alert_status_data = Alert.objects.values('status').annotate(count=Count('id'))
    
    # Preparar dados para JSON (para os gráficos)
    context = {
        'cpu_chart_data': json.dumps(list(cpu_metrics)),
        'memory_chart_data': json.dumps(list(memory_metrics)),
        'alert_severity_data': json.dumps(list(alert_severity_data)),
        'daily_alerts_data': json.dumps(list(daily_alerts)),
        'account_metrics_data': json.dumps(list(account_metrics)),
        'top_alert_resources_data': json.dumps(list(top_alert_resources)),
        'metric_types_data': json.dumps(list(metric_types)),
        'alert_status_data': json.dumps(list(alert_status_data)),
        
        # Estatísticas gerais
        'total_metrics_24h': Metric.objects.filter(timestamp__gte=start_time).count(),
        'total_alerts_24h': Alert.objects.filter(triggered_at__gte=start_time).count(),
        'active_accounts': Account.objects.filter(status='ativo').count(),
        'critical_alerts': Alert.objects.filter(
            rule__severity='critical',
            status='open'
        ).count(),
        
        # Alertas recentes
        'recent_alerts': Alert.objects.select_related('rule', 'account').order_by('-triggered_at')[:10],
        
        # Contas com mais atividade
        'active_accounts_list': account_metrics[:5],
    }
    
    return render(request, 'monitoring/advanced_dashboard.html', context)


@login_required
def metrics_api(request):
    """API para dados de métricas em tempo real"""
    metric_name = request.GET.get('metric', 'CPUUtilization')
    hours = int(request.GET.get('hours', 1))
    account_id = request.GET.get('account_id')
    
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours)
    
    metrics_query = Metric.objects.filter(
        metric_name=metric_name,
        timestamp__gte=start_time,
        timestamp__lte=end_time
    )
    
    if account_id:
        metrics_query = metrics_query.filter(account_id=account_id)
    
    metrics = metrics_query.values(
        'timestamp', 'value', 'account__nome', 'unit'
    ).order_by('timestamp')
    
    # Converter timestamps para formato JavaScript
    data = []
    for metric in metrics:
        data.append({
            'timestamp': metric['timestamp'].isoformat(),
            'value': float(metric['value']),
            'account': metric['account__nome'],
            'unit': metric['unit']
        })
    
    return JsonResponse({
        'data': data,
        'metric_name': metric_name,
        'total_points': len(data)
    })


@login_required
def alerts_api(request):
    """API para dados de alertas"""
    days = int(request.GET.get('days', 7))
    severity = request.GET.get('severity')
    status = request.GET.get('status')
    
    end_time = timezone.now()
    start_time = end_time - timedelta(days=days)
    
    alerts_query = Alert.objects.filter(
        triggered_at__gte=start_time,
        triggered_at__lte=end_time
    )
    
    if severity:
        alerts_query = alerts_query.filter(rule__severity=severity)
    
    if status:
        alerts_query = alerts_query.filter(status=status)
    
    # Agrupar por dia
    daily_data = alerts_query.extra(
        select={'day': 'date(triggered_at)'}
    ).values('day', 'rule__severity').annotate(
        count=Count('id')
    ).order_by('day', 'rule__severity')
    
    return JsonResponse({
        'data': list(daily_data),
        'total_alerts': alerts_query.count()
    })
