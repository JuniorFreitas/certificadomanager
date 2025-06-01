from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, Fieldset
from crispy_forms.bootstrap import FormActions
from .models import Certificate


class CertificateForm(forms.ModelForm):
    arquivo_upload = forms.FileField(
        label='Arquivo do Certificado',
        help_text='Selecione o arquivo do certificado (.crt, .pem, .p12, etc.)',
        required=True
    )
    
    class Meta:
        model = Certificate
        fields = [
            'versao', 'num_serie', 'alg_assin', 'alg_hash_assin', 
            'emissor', 'valid_ini', 'valid_fim', 'requerente', 
            'chave_pub', 'chave_pub_param', 'status'
        ]
        widgets = {
            'valid_ini': forms.DateInput(attrs={'type': 'date'}),
            'valid_fim': forms.DateInput(attrs={'type': 'date'}),
            'chave_pub': forms.Textarea(attrs={'rows': 4}),
            'chave_pub_param': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações Básicas',
                Row(
                    Column('versao', css_class='form-group col-md-6 mb-0'),
                    Column('num_serie', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('alg_assin', css_class='form-group col-md-6 mb-0'),
                    Column('alg_hash_assin', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'emissor',
                'requerente',
            ),
            Fieldset(
                'Validade',
                Row(
                    Column('valid_ini', css_class='form-group col-md-6 mb-0'),
                    Column('valid_fim', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'status',
            ),
            Fieldset(
                'Chaves e Arquivo',
                'chave_pub',
                'chave_pub_param',
                'arquivo_upload',
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )
    
    def save(self, commit=True):
        certificate = super().save(commit=False)
        
        # Processar arquivo upload
        if self.cleaned_data.get('arquivo_upload'):
            arquivo = self.cleaned_data['arquivo_upload']
            certificate.arquivo = arquivo.read()
        
        if commit:
            certificate.save()
        return certificate


class CertificateSearchForm(forms.Form):
    """Formulário de busca para certificados"""
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por requerente, número de série ou emissor...',
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Certificate.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    valid_fim_from = forms.DateField(
        required=False,
        label='Validade de',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    valid_fim_to = forms.DateField(
        required=False,
        label='Validade até',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    ) 