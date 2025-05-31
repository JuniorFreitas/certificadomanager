from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def resource_list(request):
    """Lista todos os recursos"""
    return render(request, 'resources/list.html')


@login_required
def resource_create(request):
    """Cria um novo recurso"""
    return render(request, 'resources/form.html')
