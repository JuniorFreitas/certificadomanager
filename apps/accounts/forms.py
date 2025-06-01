from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset, HTML, Div, Field
from crispy_forms.bootstrap import InlineRadios, PrependedText, AppendedText
from .models import Account, AccountRegion, AccountService
import re


class AccountForm(forms.ModelForm):
    """
    Formulário para criação e edição de contas AWS
    """
    
    # Campo para confirmar o secret (apenas na criação)
    confirm_secret = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirme o Secret Access Key'}),
        required=False,
        label='Confirmar Secret Access Key',
        help_text='Digite novamente o Secret Access Key para confirmação'
    )
    
    # Campo para testar conexão
    test_connection = forms.BooleanField(
        required=False,
        initial=True,
        label='Testar conexão após salvar',
        help_text='Validar credenciais AWS automaticamente'
    )
    
    class Meta:
        model = Account
        fields = [
            'nome', 'descricao', 'account_id', 'account_type',
            'access_key_id', 'secret_access_key', 'session_token',
            'default_region', 'enabled_regions', 'status',
            'max_instances', 'max_storage_gb', 'monthly_budget_usd',
            'tags'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Conta Produção AWS'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descrição da conta...'}),
            'account_id': forms.TextInput(attrs={'placeholder': '123456789012', 'pattern': r'\d{12}'}),
            'access_key_id': forms.TextInput(attrs={'placeholder': 'AKIAIOSFODNN7EXAMPLE'}),
            'secret_access_key': forms.PasswordInput(attrs={'placeholder': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'}),
            'session_token': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Token de sessão (opcional para roles temporários)'}),
            'enabled_regions': forms.CheckboxSelectMultiple(),
            'max_instances': forms.NumberInput(attrs={'min': 1, 'max': 1000}),
            'max_storage_gb': forms.NumberInput(attrs={'min': 1, 'max': 100000}),
            'monthly_budget_usd': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'tags': forms.Textarea(attrs={'rows': 3, 'placeholder': '{"ambiente": "producao", "projeto": "fcm"}'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar choices para regiões habilitadas
        self.fields['enabled_regions'].choices = Account.AWS_REGIONS
        
        # Se estamos editando, não mostrar o campo de confirmação
        if self.instance and self.instance.pk:
            self.fields['confirm_secret'].required = False
            self.fields['confirm_secret'].widget = forms.HiddenInput()
            # Limpar o campo secret para não mostrar o valor criptografado
            self.fields['secret_access_key'].widget.attrs['placeholder'] = 'Deixe em branco para manter o atual'
            self.fields['secret_access_key'].required = False
        else:
            self.fields['confirm_secret'].required = True
        
        # Configurar Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<div class="alert alert-info"><i class="bi bi-info-circle"></i> '
                 '<strong>Informações da Conta AWS:</strong> Preencha os dados da sua conta AWS. '
                 'As credenciais serão criptografadas e armazenadas com segurança.</div>'),
            
            Row(
                Column('nome', css_class='form-group col-md-8 mb-3'),
                Column('status', css_class='form-group col-md-4 mb-3'),
            ),
            
            Field('descricao', css_class='mb-3'),
            
            HTML('<h5 class="mt-4 mb-3"><i class="bi bi-aws text-warning"></i> Configurações AWS</h5>'),
            
            Row(
                Column('account_id', css_class='form-group col-md-6 mb-3'),
                Column('account_type', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<h6 class="mt-3 mb-2"><i class="bi bi-key"></i> Credenciais</h6>'),
            
            Field('access_key_id', css_class='mb-3'),
            
            Row(
                Column('secret_access_key', css_class='form-group col-md-6 mb-3'),
                Column('confirm_secret', css_class='form-group col-md-6 mb-3'),
            ),
            
            Field('session_token', css_class='mb-3'),
            
            HTML('<h6 class="mt-3 mb-2"><i class="bi bi-globe"></i> Regiões</h6>'),
            
            Row(
                Column('default_region', css_class='form-group col-md-6 mb-3'),
                Column('enabled_regions', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<h6 class="mt-3 mb-2"><i class="bi bi-gear"></i> Limites e Configurações</h6>'),
            
            Row(
                Column(AppendedText('max_instances', 'instâncias'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('max_storage_gb', 'GB'), css_class='form-group col-md-4 mb-3'),
                Column(PrependedText('monthly_budget_usd', 'USD $'), css_class='form-group col-md-4 mb-3'),
            ),
            
            Field('tags', css_class='mb-3'),
            
            HTML('<h6 class="mt-3 mb-2"><i class="bi bi-check-circle"></i> Validação</h6>'),
            
            Field('test_connection', css_class='mb-3'),
            
            HTML('<hr>'),
            
            Div(
                Submit('submit', 'Salvar Conta', css_class='btn btn-primary me-2'),
                Reset('reset', 'Limpar', css_class='btn btn-secondary me-2'),
                HTML('<a href="{% url \'accounts:list\' %}" class="btn btn-outline-secondary">Cancelar</a>'),
                css_class='d-flex justify-content-end'
            )
        )
    
    def clean_account_id(self):
        """Validar Account ID"""
        account_id = self.cleaned_data.get('account_id')
        if account_id:
            # Remover espaços e caracteres especiais
            account_id = re.sub(r'[^\d]', '', account_id)
            
            if len(account_id) != 12:
                raise ValidationError('Account ID deve ter exatamente 12 dígitos.')
            
            if not account_id.isdigit():
                raise ValidationError('Account ID deve conter apenas números.')
        
        return account_id
    
    def clean_access_key_id(self):
        """Validar Access Key ID"""
        access_key = self.cleaned_data.get('access_key_id')
        if access_key:
            # Access Key ID deve ter entre 16 e 128 caracteres e começar com AKIA ou ASIA
            if not re.match(r'^(AKIA|ASIA)[A-Z0-9]{16,}$', access_key):
                raise ValidationError('Access Key ID deve começar com AKIA ou ASIA e ter formato válido.')
        
        return access_key
    
    def clean_secret_access_key(self):
        """Validar Secret Access Key"""
        secret = self.cleaned_data.get('secret_access_key')
        
        # Se estamos editando e o campo está vazio, manter o atual
        if self.instance and self.instance.pk and not secret:
            return self.instance.secret_access_key
        
        if secret:
            # Secret deve ter pelo menos 40 caracteres
            if len(secret) < 40:
                raise ValidationError('Secret Access Key deve ter pelo menos 40 caracteres.')
        
        return secret
    
    def clean_enabled_regions(self):
        """Validar e converter regiões habilitadas para JSON"""
        enabled_regions = self.cleaned_data.get('enabled_regions')
        
        if enabled_regions:
            # Se for uma lista, converter para JSON string
            if isinstance(enabled_regions, list):
                return enabled_regions
            # Se for string, tentar fazer parse
            elif isinstance(enabled_regions, str):
                try:
                    import json
                    return json.loads(enabled_regions)
                except json.JSONDecodeError:
                    raise forms.ValidationError('Formato de regiões inválido')
        
        return []
    
    def clean(self):
        """Validação geral do formulário"""
        cleaned_data = super().clean()
        secret = cleaned_data.get('secret_access_key')
        confirm_secret = cleaned_data.get('confirm_secret')
        
        # Validar confirmação de secret apenas na criação
        if not self.instance.pk and secret and confirm_secret:
            if secret != confirm_secret:
                raise ValidationError({
                    'confirm_secret': 'Os campos Secret Access Key não coincidem.'
                })
        
        # Validar tags JSON
        tags = cleaned_data.get('tags')
        if tags:
            try:
                import json
                if isinstance(tags, str):
                    json.loads(tags)
            except json.JSONDecodeError:
                raise ValidationError({
                    'tags': 'Tags devem estar em formato JSON válido.'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Salvar com informações de auditoria"""
        instance = super().save(commit=False)
        
        if self.user:
            if not instance.pk:
                instance.usu_cad = self.user.email
            else:
                instance.usu_atu = self.user.email
                instance.data_atu = timezone.now()
        
        if commit:
            instance.save()
            
            # Testar conexão se solicitado
            if self.cleaned_data.get('test_connection'):
                try:
                    success, message = instance.test_connection()
                    if success:
                        instance.save()  # Salvar informações atualizadas da validação
                except Exception:
                    pass  # Não falhar o save se o teste falhar
        
        return instance


class AccountSearchForm(forms.Form):
    """
    Formulário para busca de contas
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por nome, account ID ou alias...',
            'class': 'form-control'
        }),
        label='Buscar'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os status')] + Account.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Status'
    )
    
    account_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + Account.ACCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo'
    )
    
    region = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas as regiões')] + Account.AWS_REGIONS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Região'
    )
    
    is_validated = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas'),
            ('true', 'Validadas'),
            ('false', 'Não validadas')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Validação'
    )


class AccountRegionForm(forms.ModelForm):
    """
    Formulário para gerenciar regiões de uma conta
    """
    
    class Meta:
        model = AccountRegion
        fields = ['region_code', 'is_enabled', 'is_default']
        widgets = {
            'region_code': forms.Select(attrs={'class': 'form-select'}),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('region_code', css_class='mb-3'),
            Field('is_enabled', css_class='mb-3'),
            Field('is_default', css_class='mb-3'),
            
            Div(
                Submit('submit', 'Salvar', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url \'accounts:detail\' account.id %}" class="btn btn-secondary">Cancelar</a>'),
                css_class='d-flex justify-content-end'
            )
        )
    
    def clean_region_code(self):
        """Validar se a região já não está cadastrada para esta conta"""
        region_code = self.cleaned_data.get('region_code')
        
        if self.account and region_code:
            existing = AccountRegion.objects.filter(
                account=self.account,
                region_code=region_code
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError('Esta região já está cadastrada para esta conta.')
        
        return region_code
    
    def save(self, commit=True):
        """Salvar com informações de auditoria"""
        instance = super().save(commit=False)
        
        if self.account:
            instance.account = self.account
        
        if self.user:
            instance.usu_cad = self.user.email
        
        if commit:
            instance.save()
        
        return instance


class AccountTestForm(forms.Form):
    """
    Formulário para testar conexão com conta AWS
    """
    service = forms.ChoiceField(
        choices=[
            ('sts', 'STS (Security Token Service)'),
            ('ec2', 'EC2 (Elastic Compute Cloud)'),
            ('s3', 'S3 (Simple Storage Service)'),
            ('iam', 'IAM (Identity and Access Management)'),
            ('rds', 'RDS (Relational Database Service)'),
            ('lambda', 'Lambda'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Serviço para Teste',
        help_text='Selecione o serviço AWS para testar a conectividade'
    )
    
    region = forms.ChoiceField(
        choices=Account.AWS_REGIONS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Região',
        help_text='Região AWS para realizar o teste'
    )
    
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        
        if self.account:
            self.fields['region'].initial = self.account.default_region
        
        # Configurar Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('service', css_class='mb-3'),
            Field('region', css_class='mb-3'),
            
            Div(
                Submit('submit', 'Testar Conexão', css_class='btn btn-primary'),
                css_class='d-flex justify-content-end'
            )
        )


class BulkAccountActionForm(forms.Form):
    """
    Formulário para ações em lote em contas
    """
    ACTION_CHOICES = [
        ('activate', 'Ativar'),
        ('deactivate', 'Desativar'),
        ('suspend', 'Suspender'),
        ('validate', 'Validar Credenciais'),
        ('delete', 'Excluir'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Ação'
    )
    
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Contas'
    )
    
    confirm = forms.BooleanField(
        required=True,
        label='Confirmo que desejo executar esta ação',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('action', css_class='mb-3'),
            Field('accounts', css_class='mb-3'),
            Field('confirm', css_class='mb-3'),
            
            Div(
                Submit('submit', 'Executar Ação', css_class='btn btn-warning'),
                css_class='d-flex justify-content-end'
            )
        ) 