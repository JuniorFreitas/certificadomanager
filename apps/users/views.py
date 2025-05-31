from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User
from .forms import UserForm


@login_required
def user_list(request):
    """Lista todos os usuários com paginação e busca"""
    search = request.GET.get('search', '')
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(nome__icontains=search) | 
            Q(email__icontains=search)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/list.html', {
        'page_obj': page_obj,
        'search': search
    })


@login_required
def user_detail(request, user_id):
    """Exibe detalhes de um usuário"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/detail.html', {'user': user})


@login_required
def user_create(request):
    """Cria um novo usuário"""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.usu_cad = request.user.email
            user.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('users:list')
    else:
        form = UserForm()
    
    return render(request, 'users/form.html', {
        'form': form,
        'title': 'Criar Usuário'
    })


@login_required
def user_edit(request, user_id):
    """Edita um usuário existente"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.usu_atu = request.user.email
            from django.utils import timezone
            user.data_atu = timezone.now()
            user.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('users:list')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'users/form.html', {
        'form': form,
        'title': 'Editar Usuário',
        'user': user
    })


@login_required
def user_delete(request, user_id):
    """Exclui um usuário"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('users:list')
    
    return render(request, 'users/delete.html', {'user': user})
