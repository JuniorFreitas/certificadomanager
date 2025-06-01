from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from apps.users.models import User
from apps.certificates.models import Certificate
from apps.accounts.models import Account
from apps.resources.models import Resource
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@login_required
def dashboard(request):
    """Dashboard principal com estatísticas"""
    
    # Estatísticas de usuários
    user_stats = {
        'total': User.objects.count(),
        'active': User.objects.filter(status=0).count(),
        'inactive': User.objects.filter(status=1).count(),
    }
    
    # Estatísticas de certificados
    cert_stats = {
        'total': Certificate.objects.count(),
        'active': Certificate.objects.filter(status=0).count(),
        'expired': Certificate.objects.filter(status=2).count(),
        'expiring_soon': Certificate.objects.filter(
            status=0,
            valid_fim__lte=timezone.now().date() + timedelta(days=30)
        ).count()
    }
    
    # Estatísticas de contas cloud
    account_stats = {
        'total': Account.objects.count(),
        'active': Account.objects.count(),  # Todas as contas são consideradas ativas
    }
    
    # Estatísticas de recursos
    resource_stats = {
        'total': Resource.objects.count(),
        'active': Resource.objects.filter(status=0).count(),
        'inactive': Resource.objects.filter(status=1).count(),
        'maintenance': Resource.objects.filter(status=2).count(),
        'by_type': Resource.objects.values('tipo').annotate(count=Count('tipo')).order_by('tipo')
    }
    
    # Certificados recentes
    recent_certificates = Certificate.objects.order_by('-data_cad')[:5]
    
    # Contas recentes
    recent_accounts = Account.objects.order_by('-data_cad')[:5]
    
    # Recursos recentes
    recent_resources = Resource.objects.select_related('account').order_by('-data_cad')[:5]
    
    # Usuários recentes
    recent_users = User.objects.order_by('-data_cad')[:5]
    
    # Certificados expirando em breve
    expiring_certificates = Certificate.objects.filter(
        status=0,
        valid_fim__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('valid_fim')[:5]
    
    context = {
        'user_stats': user_stats,
        'cert_stats': cert_stats,
        'account_stats': account_stats,
        'resource_stats': resource_stats,
        'recent_certificates': recent_certificates,
        'recent_accounts': recent_accounts,
        'recent_resources': recent_resources,
        'recent_users': recent_users,
        'expiring_certificates': expiring_certificates,
    }
    
    return render(request, 'dashboard.html', context)


def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.nome}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Email ou senha inválidos.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """View de logout"""
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('login') 