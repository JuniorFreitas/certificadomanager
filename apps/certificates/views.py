from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def certificate_list(request):
    """Lista todos os certificados"""
    return render(request, 'certificates/list.html')


@login_required
def certificate_create(request):
    """Cria um novo certificado"""
    return render(request, 'certificates/form.html')
