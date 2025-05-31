from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def account_list(request):
    """Lista todas as contas"""
    return render(request, 'accounts/list.html')


@login_required
def account_create(request):
    """Cria uma nova conta"""
    return render(request, 'accounts/form.html')
