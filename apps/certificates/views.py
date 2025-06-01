from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Certificate
from .forms import CertificateForm, CertificateSearchForm


@login_required
def certificate_list(request):
    """Lista todos os certificados com busca avançada e paginação"""
    form = CertificateSearchForm(request.GET)
    certificates = Certificate.objects.all().order_by('-data_cad')
    
    # Aplicar filtros de busca
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        valid_fim_from = form.cleaned_data.get('valid_fim_from')
        valid_fim_to = form.cleaned_data.get('valid_fim_to')
        
        if search:
            certificates = certificates.filter(
                Q(requerente__icontains=search) |
                Q(num_serie__icontains=search) |
                Q(emissor__icontains=search)
            )
        
        if status:
            certificates = certificates.filter(status=status)
        
        if valid_fim_from:
            certificates = certificates.filter(valid_fim__gte=valid_fim_from)
        
        if valid_fim_to:
            certificates = certificates.filter(valid_fim__lte=valid_fim_to)
    
    # Paginação
    paginator = Paginator(certificates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': Certificate.objects.count(),
        'active': Certificate.objects.filter(status=0).count(),
        'expired': Certificate.objects.filter(status=2).count(),
        'expiring_soon': Certificate.objects.filter(
            status=0,
            valid_fim__lte=timezone.now().date() + timezone.timedelta(days=30)
        ).count()
    }
    
    return render(request, 'certificates/list.html', {
        'page_obj': page_obj,
        'form': form,
        'stats': stats
    })


@login_required
def certificate_detail(request, certificate_id):
    """Exibe detalhes de um certificado"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    return render(request, 'certificates/detail.html', {'certificate': certificate})


@login_required
def certificate_create(request):
    """Cria um novo certificado"""
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.usu_cad = request.user.email
            certificate.save()
            messages.success(request, 'Certificado criado com sucesso!')
            return redirect('certificates:detail', certificate_id=certificate.id)
    else:
        form = CertificateForm()
    
    return render(request, 'certificates/form.html', {
        'form': form,
        'title': 'Criar Certificado'
    })


@login_required
def certificate_edit(request, certificate_id):
    """Edita um certificado existente"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.usu_atu = request.user.email
            certificate.data_atu = timezone.now()
            certificate.save()
            messages.success(request, 'Certificado atualizado com sucesso!')
            return redirect('certificates:detail', certificate_id=certificate.id)
    else:
        form = CertificateForm(instance=certificate)
    
    return render(request, 'certificates/form.html', {
        'form': form,
        'title': 'Editar Certificado',
        'certificate': certificate
    })


@login_required
def certificate_delete(request, certificate_id):
    """Exclui um certificado"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    if request.method == 'POST':
        certificate.delete()
        messages.success(request, 'Certificado excluído com sucesso!')
        return redirect('certificates:list')
    
    return render(request, 'certificates/delete.html', {'certificate': certificate})


@login_required
def certificate_download(request, certificate_id):
    """Download do arquivo do certificado"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    if not certificate.arquivo:
        messages.error(request, 'Certificado não possui arquivo anexado.')
        return redirect('certificates:detail', certificate_id=certificate.id)
    
    response = HttpResponse(certificate.arquivo, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{certificate.num_serie}.crt"'
    return response


@login_required
def certificate_expiring_soon(request):
    """Lista certificados que expiram em breve (próximos 30 dias)"""
    thirty_days_from_now = timezone.now().date() + timezone.timedelta(days=30)
    certificates = Certificate.objects.filter(
        status=0,  # Apenas ativos
        valid_fim__lte=thirty_days_from_now,
        valid_fim__gte=timezone.now().date()  # Não expirados ainda
    ).order_by('valid_fim')
    
    paginator = Paginator(certificates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'certificates/expiring_soon.html', {
        'page_obj': page_obj,
        'thirty_days_from_now': thirty_days_from_now
    })
