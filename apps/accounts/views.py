from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging

from .models import Account, AccountRegion, AccountService
from .forms import (
    AccountForm, AccountSearchForm, AccountRegionForm, 
    AccountTestForm, BulkAccountActionForm
)

logger = logging.getLogger(__name__)


@login_required
def account_list(request):
    """Lista de contas AWS com busca e filtros"""
    search_form = AccountSearchForm(request.GET)
    accounts = Account.objects.all()
    
    # Aplicar filtros de busca
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        account_type = search_form.cleaned_data.get('account_type')
        region = search_form.cleaned_data.get('region')
        is_validated = search_form.cleaned_data.get('is_validated')
        
        if search:
            accounts = accounts.filter(
                Q(nome__icontains=search) |
                Q(account_id__icontains=search) |
                Q(account_alias__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        if status:
            accounts = accounts.filter(status=status)
        
        if account_type:
            accounts = accounts.filter(account_type=account_type)
        
        if region:
            accounts = accounts.filter(default_region=region)
        
        if is_validated:
            accounts = accounts.filter(is_validated=is_validated == 'true')
    
    # Estatísticas
    stats = {
        'total': accounts.count(),
        'active': accounts.filter(status=0).count(),
        'validated': accounts.filter(is_validated=True).count(),
        'with_errors': accounts.filter(status=4).count(),
    }
    
    # Paginação
    paginator = Paginator(accounts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'stats': stats,
        'title': 'Contas AWS'
    }
    
    return render(request, 'accounts/list.html', context)


@login_required
def account_detail(request, account_id):
    """Detalhes de uma conta AWS"""
    account = get_object_or_404(Account, id=account_id)
    
    # Obter informações da conta AWS (se validada)
    account_info = None
    resource_summary = None
    available_services = []
    
    if account.is_validated:
        try:
            account_info = account.get_account_info()
            resource_summary = account.get_resource_summary()
            available_services = account.get_available_services()
        except Exception as e:
            logger.error(f"Erro ao obter informações da conta {account.id}: {str(e)}")
            messages.warning(request, f"Erro ao obter informações da AWS: {str(e)}")
    
    # Regiões da conta
    regions = account.regions.all()
    
    # Serviços da conta
    services = account.services.all()
    
    context = {
        'account': account,
        'account_info': account_info,
        'resource_summary': resource_summary,
        'available_services': available_services,
        'regions': regions,
        'services': services,
        'title': f'Conta AWS - {account.nome}'
    }
    
    return render(request, 'accounts/detail.html', context)


@login_required
def account_create(request):
    """Criar nova conta AWS"""
    if request.method == 'POST':
        form = AccountForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                account = form.save()
                messages.success(request, f'Conta AWS "{account.nome}" criada com sucesso!')
                
                # Se o teste de conexão foi solicitado e falhou, mostrar aviso
                if form.cleaned_data.get('test_connection') and not account.is_validated:
                    messages.warning(
                        request, 
                        'Conta criada, mas a validação das credenciais falhou. '
                        'Verifique as credenciais e teste a conexão novamente.'
                    )
                
                return redirect('accounts:detail', account_id=account.id)
            except Exception as e:
                logger.error(f"Erro ao criar conta: {str(e)}")
                messages.error(request, f'Erro ao criar conta: {str(e)}')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados informados.')
    else:
        form = AccountForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Nova Conta AWS'
    }
    
    return render(request, 'accounts/form.html', context)


@login_required
def account_edit(request, account_id):
    """Editar conta AWS"""
    account = get_object_or_404(Account, id=account_id)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account, user=request.user)
        if form.is_valid():
            try:
                account = form.save()
                messages.success(request, f'Conta AWS "{account.nome}" atualizada com sucesso!')
                
                # Se o teste de conexão foi solicitado e falhou, mostrar aviso
                if form.cleaned_data.get('test_connection') and not account.is_validated:
                    messages.warning(
                        request, 
                        'Conta atualizada, mas a validação das credenciais falhou. '
                        'Verifique as credenciais e teste a conexão novamente.'
                    )
                
                return redirect('accounts:detail', account_id=account.id)
            except Exception as e:
                logger.error(f"Erro ao atualizar conta: {str(e)}")
                messages.error(request, f'Erro ao atualizar conta: {str(e)}')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados informados.')
    else:
        form = AccountForm(instance=account, user=request.user)
    
    context = {
        'form': form,
        'account': account,
        'title': f'Editar Conta AWS - {account.nome}'
    }
    
    return render(request, 'accounts/form.html', context)


@login_required
def account_delete(request, account_id):
    """Excluir conta AWS"""
    account = get_object_or_404(Account, id=account_id)
    
    if request.method == 'POST':
        try:
            account_name = account.nome
            account.delete()
            messages.success(request, f'Conta AWS "{account_name}" excluída com sucesso!')
            return redirect('accounts:list')
        except Exception as e:
            logger.error(f"Erro ao excluir conta: {str(e)}")
            messages.error(request, f'Erro ao excluir conta: {str(e)}')
            return redirect('accounts:detail', account_id=account.id)
    
    context = {
        'account': account,
        'title': f'Excluir Conta AWS - {account.nome}'
    }
    
    return render(request, 'accounts/delete.html', context)


@login_required
def account_test(request, account_id):
    """Testar conexão com conta AWS"""
    account = get_object_or_404(Account, id=account_id)
    
    if request.method == 'POST':
        form = AccountTestForm(request.POST, account=account)
        if form.is_valid():
            service = form.cleaned_data['service']
            region = form.cleaned_data['region']
            
            try:
                # Testar conexão específica
                if service == 'sts':
                    client = account.get_boto3_client('sts', region)
                    response = client.get_caller_identity()
                    result = {
                        'success': True,
                        'message': 'Conexão STS bem-sucedida',
                        'data': {
                            'Account': response.get('Account'),
                            'UserId': response.get('UserId'),
                            'Arn': response.get('Arn')
                        }
                    }
                elif service == 'ec2':
                    client = account.get_boto3_client('ec2', region)
                    response = client.describe_regions()
                    result = {
                        'success': True,
                        'message': f'Conexão EC2 bem-sucedida. {len(response["Regions"])} regiões disponíveis',
                        'data': {'regions_count': len(response["Regions"])}
                    }
                elif service == 's3':
                    client = account.get_boto3_client('s3', region)
                    response = client.list_buckets()
                    result = {
                        'success': True,
                        'message': f'Conexão S3 bem-sucedida. {len(response["Buckets"])} buckets encontrados',
                        'data': {'buckets_count': len(response["Buckets"])}
                    }
                else:
                    # Teste genérico para outros serviços
                    client = account.get_boto3_client(service, region)
                    result = {
                        'success': True,
                        'message': f'Cliente {service.upper()} criado com sucesso',
                        'data': {'service': service, 'region': region}
                    }
                
                messages.success(request, result['message'])
                
                # Atualizar status da conta se o teste foi bem-sucedido
                if result['success'] and service == 'sts':
                    account.is_validated = True
                    account.last_validation = timezone.now()
                    account.validation_error = None
                    account.status = 0  # Ativa
                    account.save()
                
            except Exception as e:
                logger.error(f"Erro no teste de conexão: {str(e)}")
                result = {
                    'success': False,
                    'message': f'Erro no teste de conexão: {str(e)}',
                    'data': None
                }
                messages.error(request, result['message'])
                
                # Atualizar status da conta se o teste falhou
                account.is_validated = False
                account.validation_error = str(e)
                account.status = 4  # Erro de Conexão
                account.save()
            
            # Se for uma requisição AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(result)
            
            return redirect('accounts:detail', account_id=account.id)
    else:
        form = AccountTestForm(account=account)
    
    context = {
        'form': form,
        'account': account,
        'title': f'Testar Conexão - {account.nome}'
    }
    
    return render(request, 'accounts/test.html', context)


@login_required
def account_validate(request, account_id):
    """Validar credenciais da conta AWS"""
    account = get_object_or_404(Account, id=account_id)
    
    try:
        success, message = account.validate_credentials()
        
        if success:
            account.save()  # Salvar informações atualizadas
            messages.success(request, f'Credenciais validadas com sucesso: {message}')
        else:
            account.save()  # Salvar erro de validação
            messages.error(request, f'Erro na validação: {message}')
    
    except Exception as e:
        logger.error(f"Erro na validação da conta {account.id}: {str(e)}")
        messages.error(request, f'Erro inesperado na validação: {str(e)}')
    
    return redirect('accounts:detail', account_id=account.id)


@login_required
def account_resources(request, account_id):
    """Visualizar recursos da conta AWS"""
    account = get_object_or_404(Account, id=account_id)
    
    if not account.is_validated:
        messages.warning(request, 'Conta não validada. Valide as credenciais primeiro.')
        return redirect('accounts:detail', account_id=account.id)
    
    try:
        resource_summary = account.get_resource_summary()
        
        # Obter informações detalhadas se solicitado
        detailed_info = {}
        
        if request.GET.get('detailed') == 'true':
            # EC2 Instances detalhadas
            if 'ec2_instances' in resource_summary:
                try:
                    ec2_client = account.get_boto3_client('ec2')
                    instances = ec2_client.describe_instances()
                    detailed_info['ec2_instances'] = []
                    
                    for reservation in instances['Reservations']:
                        for instance in reservation['Instances']:
                            detailed_info['ec2_instances'].append({
                                'InstanceId': instance.get('InstanceId'),
                                'InstanceType': instance.get('InstanceType'),
                                'State': instance.get('State', {}).get('Name'),
                                'LaunchTime': instance.get('LaunchTime'),
                                'PrivateIpAddress': instance.get('PrivateIpAddress'),
                                'PublicIpAddress': instance.get('PublicIpAddress'),
                            })
                except Exception as e:
                    logger.error(f"Erro ao obter detalhes EC2: {str(e)}")
            
            # S3 Buckets detalhados
            if 's3_buckets' in resource_summary:
                try:
                    s3_client = account.get_boto3_client('s3')
                    buckets = s3_client.list_buckets()
                    detailed_info['s3_buckets'] = []
                    
                    for bucket in buckets['Buckets']:
                        detailed_info['s3_buckets'].append({
                            'Name': bucket.get('Name'),
                            'CreationDate': bucket.get('CreationDate'),
                        })
                except Exception as e:
                    logger.error(f"Erro ao obter detalhes S3: {str(e)}")
        
        context = {
            'account': account,
            'resource_summary': resource_summary,
            'detailed_info': detailed_info,
            'title': f'Recursos AWS - {account.nome}'
        }
        
        return render(request, 'accounts/resources.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao obter recursos da conta {account.id}: {str(e)}")
        messages.error(request, f'Erro ao obter recursos: {str(e)}')
        return redirect('accounts:detail', account_id=account.id)


@login_required
def bulk_actions(request):
    """Ações em lote para contas"""
    if request.method == 'POST':
        form = BulkAccountActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            accounts = form.cleaned_data['accounts']
            
            success_count = 0
            error_count = 0
            
            for account in accounts:
                try:
                    if action == 'activate':
                        account.status = 0
                        account.save()
                        success_count += 1
                    elif action == 'deactivate':
                        account.status = 1
                        account.save()
                        success_count += 1
                    elif action == 'suspend':
                        account.status = 2
                        account.save()
                        success_count += 1
                    elif action == 'validate':
                        success, message = account.validate_credentials()
                        if success:
                            account.save()
                            success_count += 1
                        else:
                            error_count += 1
                    elif action == 'delete':
                        account.delete()
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"Erro na ação em lote para conta {account.id}: {str(e)}")
                    error_count += 1
            
            if success_count > 0:
                messages.success(request, f'Ação executada com sucesso em {success_count} conta(s).')
            
            if error_count > 0:
                messages.error(request, f'Erro ao executar ação em {error_count} conta(s).')
            
            return redirect('accounts:list')
    else:
        form = BulkAccountActionForm()
    
    context = {
        'form': form,
        'title': 'Ações em Lote - Contas AWS'
    }
    
    return render(request, 'accounts/bulk_actions.html', context)


# API Views para AJAX

@login_required
@require_http_methods(["GET"])
def api_account_status(request, account_id):
    """API para obter status da conta"""
    account = get_object_or_404(Account, id=account_id)
    
    data = {
        'id': account.id,
        'nome': account.nome,
        'status': account.status,
        'status_display': account.status_display,
        'is_validated': account.is_validated,
        'last_validation': account.last_validation.isoformat() if account.last_validation else None,
        'validation_error': account.validation_error,
    }
    
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def api_quick_validate(request, account_id):
    """API para validação rápida de conta"""
    account = get_object_or_404(Account, id=account_id)
    
    try:
        success, message = account.validate_credentials()
        
        if success:
            account.save()
        
        return JsonResponse({
            'success': success,
            'message': message,
            'status': account.status,
            'is_validated': account.is_validated,
            'last_validation': account.last_validation.isoformat() if account.last_validation else None,
        })
        
    except Exception as e:
        logger.error(f"Erro na validação rápida da conta {account.id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Erro inesperado: {str(e)}',
            'status': account.status,
            'is_validated': account.is_validated,
        })


@login_required
@require_http_methods(["GET"])
def api_account_resources(request, account_id):
    """API para obter resumo de recursos da conta"""
    account = get_object_or_404(Account, id=account_id)
    
    if not account.is_validated:
        return JsonResponse({
            'success': False,
            'message': 'Conta não validada'
        })
    
    try:
        resource_summary = account.get_resource_summary()
        
        return JsonResponse({
            'success': True,
            'data': resource_summary
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter recursos da conta {account.id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


# Views para gerenciar regiões

@login_required
def region_create(request, account_id):
    """Adicionar região à conta"""
    account = get_object_or_404(Account, id=account_id)
    
    if request.method == 'POST':
        form = AccountRegionForm(request.POST, account=account, user=request.user)
        if form.is_valid():
            try:
                region = form.save()
                messages.success(request, f'Região {region.get_region_code_display()} adicionada com sucesso!')
                return redirect('accounts:detail', account_id=account.id)
            except Exception as e:
                logger.error(f"Erro ao adicionar região: {str(e)}")
                messages.error(request, f'Erro ao adicionar região: {str(e)}')
    else:
        form = AccountRegionForm(account=account, user=request.user)
    
    context = {
        'form': form,
        'account': account,
        'title': f'Adicionar Região - {account.nome}'
    }
    
    return render(request, 'accounts/region_form.html', context)


@login_required
def region_delete(request, account_id, region_id):
    """Remover região da conta"""
    account = get_object_or_404(Account, id=account_id)
    region = get_object_or_404(AccountRegion, id=region_id, account=account)
    
    if request.method == 'POST':
        try:
            region_name = region.get_region_code_display()
            region.delete()
            messages.success(request, f'Região {region_name} removida com sucesso!')
        except Exception as e:
            logger.error(f"Erro ao remover região: {str(e)}")
            messages.error(request, f'Erro ao remover região: {str(e)}')
        
        return redirect('accounts:detail', account_id=account.id)
    
    context = {
        'account': account,
        'region': region,
        'title': f'Remover Região - {account.nome}'
    }
    
    return render(request, 'accounts/region_delete.html', context)
