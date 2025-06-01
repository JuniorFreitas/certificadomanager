from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, Fieldset
from crispy_forms.bootstrap import FormActions
from .models import Resource
from apps.accounts.models import Account


class ResourceForm(forms.ModelForm):
    """Formulário para criação e edição de recursos"""
    
    # Campo para associar com conta cloud
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        label='Conta Cloud',
        help_text='Selecione a conta cloud onde o recurso está hospedado',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Resource
        fields = ['nome', 'tipo', 'url', 'account', 'status', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do recurso'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://exemplo.com'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descrição opcional do recurso'}),
        }
        help_texts = {
            'nome': 'Nome descritivo para identificar o recurso',
            'tipo': 'Tipo do recurso AWS',
            'url': 'URL de acesso ao recurso',
            'status': 'Status atual do recurso',
            'descricao': 'Descrição opcional com detalhes do recurso',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações Básicas',
                'nome',
                Row(
                    Column('tipo', css_class='form-group col-md-6 mb-0'),
                    Column('status', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'url',
                'account',
            ),
            Fieldset(
                'Informações Adicionais',
                'descricao',
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )
    
    def clean_url(self):
        """Valida a URL do recurso"""
        url = self.cleaned_data.get('url')
        if url:
            # Verificar se é uma URL válida
            if not url.startswith(('http://', 'https://')):
                raise forms.ValidationError('URL deve começar com http:// ou https://')
        return url
    
    def clean(self):
        """Validação geral do formulário"""
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        url = cleaned_data.get('url')
        
        # Validações específicas por tipo de recurso
        if tipo is not None and url:
            tipo_display = dict(Resource.RESOURCE_TYPE_CHOICES)[tipo]
            
            # Validações específicas para S3
            if tipo == 0:  # S3
                if 's3' not in url.lower():
                    raise forms.ValidationError(f'URL deve conter "s3" para recursos do tipo {tipo_display}')
            
            # Validações específicas para CloudFront
            elif tipo == 2:  # CloudFront
                if 'cloudfront' not in url.lower():
                    raise forms.ValidationError(f'URL deve conter "cloudfront" para recursos do tipo {tipo_display}')
        
        return cleaned_data


class ResourceSearchForm(forms.Form):
    """Formulário de busca para recursos"""
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por nome ou URL...',
            'class': 'form-control'
        })
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Resource.RESOURCE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Resource.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        empty_label='Todas as contas',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-3 mb-0'),
                Column('tipo', css_class='form-group col-md-2 mb-0'),
                Column('status', css_class='form-group col-md-2 mb-0'),
                Column('account', css_class='form-group col-md-3 mb-0'),
                Column(
                    Submit('submit', 'Buscar', css_class='btn btn-outline-primary w-100'),
                    css_class='form-group col-md-2 mb-0'
                ),
                css_class='form-row'
            )
        ) 