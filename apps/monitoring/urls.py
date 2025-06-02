from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Dashboard principal
    path('', views.monitoring_dashboard, name='dashboard'),
    path('advanced/', views.advanced_dashboard, name='advanced_dashboard'),
    
    # APIs para dados em tempo real
    path('api/metrics/', views.metrics_api, name='metrics_api'),
    path('api/alerts/', views.alerts_api, name='alerts_api'),
    path('api/collect-metrics/', views.api_collect_metrics, name='api_collect_metrics'),
    
    # Alertas
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<uuid:alert_id>/', views.alert_detail, name='alert_detail'),
    path('alerts/<uuid:alert_id>/acknowledge/', views.alert_acknowledge, name='alert_acknowledge'),
    path('alerts/<uuid:alert_id>/resolve/', views.alert_resolve, name='alert_resolve'),
    
    # Regras de Alerta
    path('rules/', views.alert_rule_list, name='alert_rule_list'),
    path('rules/create/', views.alert_rule_create, name='alert_rule_create'),
    path('rules/<uuid:rule_id>/edit/', views.alert_rule_edit, name='alert_rule_edit'),
    path('rules/<uuid:rule_id>/delete/', views.alert_rule_delete, name='alert_rule_delete'),
    
    # Métricas
    path('metrics/', views.metrics_view, name='metrics'),
    
    # Alertas de Custo
    path('cost-alerts/', views.cost_alerts_list, name='cost_alerts_list'),
    path('cost-alerts/create/', views.cost_alert_create, name='cost_alert_create'),
] 