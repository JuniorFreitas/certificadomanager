from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.monitoring.services import MetricCollectionService, AlertService
from apps.accounts.models import Account
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Coleta métricas AWS para todas as contas ativas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--account-id',
            type=str,
            help='ID específico da conta AWS para coletar métricas',
        )
        parser.add_argument(
            '--check-alerts',
            action='store_true',
            help='Verificar regras de alerta após coleta',
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
                self.style.SUCCESS(f'🚀 Iniciando coleta de métricas em {start_time}')
            )

        # Filtrar contas
        if options['account_id']:
            try:
                accounts = [Account.objects.get(id=options['account_id'])]
                if options['verbose']:
                    self.stdout.write(f'📊 Coletando métricas para conta específica: {accounts[0].nome}')
            except Account.DoesNotExist:
                raise CommandError(f'Conta com ID {options["account_id"]} não encontrada')
        else:
            accounts = Account.objects.filter(status='ativo')
            if options['verbose']:
                self.stdout.write(f'📊 Coletando métricas para {accounts.count()} contas ativas')

        total_metrics = 0
        successful_accounts = 0
        failed_accounts = 0

        for account in accounts:
            try:
                if options['verbose']:
                    self.stdout.write(f'  🔄 Processando conta: {account.nome}')
                
                metrics_collected = MetricCollectionService.collect_metrics_for_account(account)
                total_metrics += metrics_collected['total']
                successful_accounts += 1
                
                if options['verbose']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    ✅ {metrics_collected["total"]} métricas coletadas '
                            f'(EC2: {metrics_collected["ec2"]}, '
                            f'RDS: {metrics_collected["rds"]}, '
                            f'Lambda: {metrics_collected["lambda"]}, '
                            f'S3: {metrics_collected["s3"]})'
                        )
                    )
                
            except Exception as e:
                failed_accounts += 1
                error_msg = f'❌ Erro ao coletar métricas para {account.nome}: {str(e)}'
                
                if options['verbose']:
                    self.stdout.write(self.style.ERROR(f'    {error_msg}'))
                
                logger.error(error_msg)

        # Verificar alertas se solicitado
        alerts_triggered = 0
        if options['check_alerts']:
            if options['verbose']:
                self.stdout.write('🚨 Verificando regras de alerta...')
            
            try:
                alerts_triggered = AlertService.check_alert_rules()
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠️ {alerts_triggered} alertas disparados')
                    )
            except Exception as e:
                error_msg = f'Erro ao verificar alertas: {str(e)}'
                self.stdout.write(self.style.ERROR(f'    ❌ {error_msg}'))
                logger.error(error_msg)

        # Resumo final
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📈 RESUMO DA COLETA DE MÉTRICAS'))
        self.stdout.write('='*60)
        self.stdout.write(f'⏱️  Duração: {duration:.2f} segundos')
        self.stdout.write(f'🏢 Contas processadas: {successful_accounts + failed_accounts}')
        self.stdout.write(f'✅ Sucessos: {successful_accounts}')
        self.stdout.write(f'❌ Falhas: {failed_accounts}')
        self.stdout.write(f'📊 Total de métricas coletadas: {total_metrics}')
        
        if options['check_alerts']:
            self.stdout.write(f'🚨 Alertas disparados: {alerts_triggered}')
        
        self.stdout.write('='*60)
        
        if failed_accounts > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ {failed_accounts} conta(s) falharam. Verifique os logs para detalhes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('🎉 Todas as contas foram processadas com sucesso!')
            ) 