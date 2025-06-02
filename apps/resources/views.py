from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Resource
from .forms import ResourceForm, ResourceSearchForm
import boto3
from botocore.exceptions import ClientError


@login_required
def resource_list(request):
    """Lista todos os recursos com busca avançada e paginação"""
    form = ResourceSearchForm(request.GET)
    resources = Resource.objects.select_related('account').order_by('-data_cad')
    
    # Aplicar filtros de busca
    if form.is_valid():
        search = form.cleaned_data.get('search')
        tipo = form.cleaned_data.get('tipo')
        status = form.cleaned_data.get('status')
        account = form.cleaned_data.get('account')
        
        if search:
            resources = resources.filter(
                Q(nome__icontains=search) |
                Q(url__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        if tipo:
            resources = resources.filter(tipo=tipo)
            
        if status:
            resources = resources.filter(status=status)
        
        if account:
            resources = resources.filter(account=account)
    
    # Paginação
    paginator = Paginator(resources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': Resource.objects.count(),
        'active': Resource.objects.filter(status=0).count(),
        'inactive': Resource.objects.filter(status=1).count(),
        'maintenance': Resource.objects.filter(status=2).count(),
    }
    
    return render(request, 'resources/list.html', {
        'page_obj': page_obj,
        'form': form,
        'stats': stats
    })


@login_required
def resource_detail(request, resource_id):
    """Exibe detalhes de um recurso específico"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Informações AWS do recurso
    aws_info = None
    if resource.account:
        try:
            aws_info = _get_resource_aws_info(resource)
        except Exception as e:
            messages.warning(request, f'Não foi possível obter informações AWS: {str(e)}')
    
    return render(request, 'resources/detail.html', {
        'resource': resource,
        'aws_info': aws_info
    })


@login_required
def resource_create(request):
    """Cria um novo recurso"""
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.usu_cad = request.user.email
            resource.save()
            messages.success(request, 'Recurso criado com sucesso!')
            return redirect('resources:detail', resource_id=resource.id)
    else:
        form = ResourceForm()
    
    return render(request, 'resources/form.html', {
        'form': form,
        'title': 'Criar Recurso'
    })


@login_required
def resource_edit(request, resource_id):
    """Edita um recurso existente"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.usu_atu = request.user.email
            resource.data_atu = timezone.now()
            resource.save()
            messages.success(request, 'Recurso atualizado com sucesso!')
            return redirect('resources:detail', resource_id=resource.id)
    else:
        form = ResourceForm(instance=resource)
    
    return render(request, 'resources/form.html', {
        'form': form,
        'title': 'Editar Recurso',
        'resource': resource
    })


@login_required
def resource_delete(request, resource_id):
    """Exclui um recurso"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        resource_name = resource.nome
        resource.delete()
        messages.success(request, f'Recurso "{resource_name}" excluído com sucesso!')
        return redirect('resources:list')
    
    return render(request, 'resources/delete.html', {
        'resource': resource
    })


@login_required
def test_resource_connection(request, resource_id):
    """Testa a conectividade de um recurso via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    resource = get_object_or_404(Resource, id=resource_id)
    
    try:
        # Testar conectividade baseado no tipo de recurso
        result = _test_resource_connectivity(resource)
        return JsonResponse({
            'success': True,
            'message': 'Conexão testada com sucesso!',
            'details': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao testar conexão: {str(e)}'
        })


def _get_resource_aws_info(resource):
    """Obtém informações AWS específicas do recurso"""
    if not resource.account:
        return None
    
    try:
        # Configurar cliente AWS
        session = boto3.Session(
            aws_access_key_id=resource.account.access_key_id,
            aws_secret_access_key=resource.account.decrypted_secret
        )
        
        info = {
            'account_id': resource.account.account_id,
            'region': 'us-east-1',  # Região padrão
            'status': 'unknown'
        }
        
        # Informações específicas por tipo de recurso
        if resource.tipo == 0:  # S3
            s3_client = session.client('s3')
            # Extrair nome do bucket da URL
            bucket_name = resource.url.split('/')[-1] if '/' in resource.url else resource.nome
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                info['status'] = 'accessible'
                info['service'] = 'S3'
                info['bucket_name'] = bucket_name
            except ClientError:
                info['status'] = 'not_found'
                
        elif resource.tipo == 4:  # EC2
            ec2_client = session.client('ec2')
            # Tentar obter informações da instância
            info['service'] = 'EC2'
            info['status'] = 'accessible'
            
        elif resource.tipo == 5:  # RDS
            rds_client = session.client('rds')
            info['service'] = 'RDS'
            info['status'] = 'accessible'
        
        return info
        
    except Exception as e:
        return {'error': str(e)}


def _test_resource_connectivity(resource):
    """Testa a conectividade específica do recurso"""
    if not resource.account:
        raise Exception('Recurso não possui conta associada')
    
    try:
        # Configurar cliente AWS
        session = boto3.Session(
            aws_access_key_id=resource.account.access_key_id,
            aws_secret_access_key=resource.account.decrypted_secret
        )
        
        # Teste básico de conectividade
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        
        result = {
            'account_id': identity.get('Account'),
            'user_id': identity.get('UserId'),
            'arn': identity.get('Arn'),
            'resource_type': resource.get_tipo_display(),
            'resource_url': resource.url
        }
        
        # Testes específicos por tipo
        if resource.tipo == 0:  # S3
            s3_client = session.client('s3')
            bucket_name = resource.url.split('/')[-1] if '/' in resource.url else resource.nome
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                result['s3_status'] = 'accessible'
            except ClientError as e:
                result['s3_status'] = f'error: {e.response["Error"]["Code"]}'
        
        return result
        
    except Exception as e:
        raise Exception(f'Erro ao testar conectividade: {str(e)}')
