from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, Fieldset
from crispy_forms.bootstrap import FormActions
from .models import AlertRule, CostAlert, MonitoringDashboard
from apps.accounts.models import Account


class AlertRuleForm(forms.ModelForm):
    """Formulário para criação e edição de regras de alerta"""
    
    class Meta:
        model = AlertRule
        fields = [
            'name', 'description', 'account', 'metric', 'operator', 
            'threshold', 'severity', 'is_enabled', 'check_interval', 
            'cooldown_period', 'notify_email', 'notify_slack', 'slack_webhook'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'slack_webhook': forms.URLInput(attrs={'placeholder': 'https://hooks.slack.com/...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações Básicas',
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('account', css_class='form-group col-md-6 mb-3'),
                ),
                'description',
            ),
            Fieldset(
                'Configurações da Métrica',
                Row(
                    Column('metric', css_class='form-group col-md-4 mb-3'),
                    Column('operator', css_class='form-group col-md-4 mb-3'),
                    Column('threshold', css_class='form-group col-md-4 mb-3'),
                ),
                Row(
                    Column('severity', css_class='form-group col-md-6 mb-3'),
                    Column('is_enabled', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                'Configurações de Verificação',
                Row(
                    Column('check_interval', css_class='form-group col-md-6 mb-3'),
                    Column('cooldown_period', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                'Notificações',
                Row(
                    Column('notify_email', css_class='form-group col-md-6 mb-3'),
                    Column('notify_slack', css_class='form-group col-md-6 mb-3'),
                ),
                'slack_webhook',
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )


class CostAlertForm(forms.ModelForm):
    """Formulário para criação e edição de alertas de custo"""
    
    class Meta:
        model = CostAlert
        fields = ['name', 'account', 'threshold', 'period', 'is_enabled', 'notify_email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações do Alerta de Custo',
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('account', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('threshold', css_class='form-group col-md-6 mb-3'),
                    Column('period', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('is_enabled', css_class='form-group col-md-6 mb-3'),
                    Column('notify_email', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )


class MonitoringDashboardForm(forms.ModelForm):
    """Formulário para criação e edição de dashboards"""
    
    class Meta:
        model = MonitoringDashboard
        fields = ['name', 'description', 'is_default']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações do Dashboard',
                'name',
                'description',
                'is_default',
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )


class AlertSearchForm(forms.Form):
    """Formulário de busca para alertas"""
    
    STATUS_CHOICES = [
        ('', 'Todos os Status'),
        ('open', 'Aberto'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
        ('suppressed', 'Suprimido'),
    ]
    
    SEVERITY_CHOICES = [
        ('', 'Todas as Severidades'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    severity = forms.ChoiceField(
        choices=SEVERITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        empty_label='Todas as Contas',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='form-group col-md-4'),
                Column('severity', css_class='form-group col-md-4'),
                Column('account', css_class='form-group col-md-4'),
            ),
            FormActions(
                Submit('submit', 'Filtrar', css_class='btn btn-primary'),
                HTML('<a href="?" class="btn btn-secondary ms-2">Limpar</a>'),
            )
        )


class MetricsFilterForm(forms.Form):
    """Formulário de filtros para métricas"""
    
    PERIOD_CHOICES = [
        ('1h', 'Última Hora'),
        ('6h', 'Últimas 6 Horas'),
        ('24h', 'Últimas 24 Horas'),
        ('7d', 'Últimos 7 Dias'),
    ]
    
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        empty_label='Todas as Contas',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    metric = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da métrica...'
        })
    )
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='24h',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('account', css_class='form-group col-md-4'),
                Column('metric', css_class='form-group col-md-4'),
                Column('period', css_class='form-group col-md-4'),
            ),
            FormActions(
                Submit('submit', 'Aplicar Filtros', css_class='btn btn-primary'),
                HTML('<a href="?" class="btn btn-secondary ms-2">Limpar</a>'),
            )
        ) 