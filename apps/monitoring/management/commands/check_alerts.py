from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.monitoring.services import AlertService
from apps.monitoring.models import AlertRule, Alert
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica regras de alerta e dispara notificações'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rule-id',
            type=str,
            help='ID específico da regra de alerta para verificar',
        )
        parser.add_argument(
            '--resolve-old',
            action='store_true',
            help='Resolver automaticamente alertas antigos (mais de 24h)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular verificação sem disparar alertas reais',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Saída detalhada',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS(f'🚨 Iniciando verificação de alertas em {start_time}')
            )

        # Resolver alertas antigos se solicitado
        if options['resolve_old']:
            self._resolve_old_alerts(options['verbose'])

        # Filtrar regras
        if options['rule_id']:
            try:
                rules = [AlertRule.objects.get(id=options['rule_id'])]
                if options['verbose']:
                    self.stdout.write(f'🔍 Verificando regra específica: {rules[0].name}')
            except AlertRule.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Regra com ID {options["rule_id"]} não encontrada')
                )
                return
        else:
            rules = AlertRule.objects.filter(is_enabled=True)
            if options['verbose']:
                self.stdout.write(f'🔍 Verificando {rules.count()} regras ativas')

        alerts_triggered = 0
        rules_checked = 0
        errors = 0

        for rule in rules:
            try:
                rules_checked += 1
                
                if options['verbose']:
                    self.stdout.write(f'  🔄 Verificando regra: {rule.name}')
                
                if options['dry_run']:
                    # Simular verificação
                    should_trigger = AlertService._should_trigger_alert(rule)
                    if should_trigger:
                        alerts_triggered += 1
                        if options['verbose']:
                            self.stdout.write(
                                self.style.WARNING(f'    ⚠️ [DRY-RUN] Alerta seria disparado')
                            )
                    else:
                        if options['verbose']:
                            self.stdout.write(f'    ✅ Condições normais')
                else:
                    # Verificação real
                    if AlertService._should_trigger_alert(rule):
                        AlertService._trigger_alert(rule)
                        alerts_triggered += 1
                        if options['verbose']:
                            self.stdout.write(
                                self.style.WARNING(f'    🚨 Alerta disparado!')
                            )
                    else:
                        if options['verbose']:
                            self.stdout.write(f'    ✅ Condições normais')
                
            except Exception as e:
                errors += 1
                error_msg = f'❌ Erro ao verificar regra {rule.name}: {str(e)}'
                
                if options['verbose']:
                    self.stdout.write(self.style.ERROR(f'    {error_msg}'))
                
                logger.error(error_msg)

        # Resumo final
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🚨 RESUMO DA VERIFICAÇÃO DE ALERTAS'))
        self.stdout.write('='*60)
        self.stdout.write(f'⏱️  Duração: {duration:.2f} segundos')
        self.stdout.write(f'🔍 Regras verificadas: {rules_checked}')
        self.stdout.write(f'🚨 Alertas disparados: {alerts_triggered}')
        self.stdout.write(f'❌ Erros: {errors}')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('🧪 Modo DRY-RUN - Nenhum alerta real foi disparado'))
        
        self.stdout.write('='*60)
        
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ {errors} erro(s) ocorreram. Verifique os logs para detalhes.'
                )
            )
        elif alerts_triggered > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️ {alerts_triggered} alerta(s) foram disparados!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Todas as verificações passaram sem alertas!')
            )

    def _resolve_old_alerts(self, verbose=False):
        """Resolve alertas antigos automaticamente"""
        cutoff_time = timezone.now() - timezone.timedelta(hours=24)
        
        old_alerts = Alert.objects.filter(
            status='open',
            triggered_at__lt=cutoff_time
        )
        
        count = old_alerts.count()
        
        if count > 0:
            if verbose:
                self.stdout.write(f'🔄 Resolvendo {count} alertas antigos...')
            
            for alert in old_alerts:
                alert.resolve('system_auto_resolve')
                if verbose:
                    self.stdout.write(f'    ✅ Resolvido: {alert.rule.name}')
            
            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {count} alertas antigos resolvidos automaticamente')
                )
        else:
            if verbose:
                self.stdout.write('ℹ️ Nenhum alerta antigo para resolver') 