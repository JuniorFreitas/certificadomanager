from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def permission_list(request):
    """Lista todas as permissões"""
    return render(request, 'permissions/list.html')


@login_required
def permission_create(request):
    """Cria uma nova permissão"""
    return render(request, 'permissions/form.html')
