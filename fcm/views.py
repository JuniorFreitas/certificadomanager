from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from apps.users.models import User
from apps.certificates.models import Certificate
from apps.accounts.models import Account
from apps.resources.models import Resource


@login_required
def dashboard(request):
    """Dashboard principal com estatísticas"""
    context = {
        'total_users': User.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'total_accounts': Account.objects.count(),
        'total_resources': Resource.objects.count(),
        'active_certificates': Certificate.objects.filter(status=0).count(),
        'expired_certificates': Certificate.objects.filter(status=2).count(),
        'recent_certificates': Certificate.objects.order_by('-data_cad')[:5],
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
            return redirect('dashboard')
        else:
            messages.error(request, 'Email ou senha inválidos.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """View de logout"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('login') 