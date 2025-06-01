from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, Fieldset, HTML
from crispy_forms.bootstrap import FormActions
from .models import Permission, Role, UserRole
from apps.users.models import User


class PermissionForm(forms.ModelForm):
    """Formulário para criação e edição de permissões"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(status=0),  # Apenas usuários ativos
        label='Usuário',
        help_text='Selecione o usuário para conceder/revogar a permissão',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Permission
        fields = ['user', 'permission_type', 'granted']
        widgets = {
            'permission_type': forms.Select(attrs={'class': 'form-control'}),
            'granted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'permission_type': 'Tipo de permissão a ser concedida ou revogada',
            'granted': 'Marque para conceder a permissão, desmarque para revogar',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações da Permissão',
                'user',
                'permission_type',
                HTML('<div class="form-check mt-3">'),
                'granted',
                HTML('</div>'),
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )
    
    def clean(self):
        """Validação customizada"""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        permission_type = cleaned_data.get('permission_type')
        
        # Verificar se já existe uma permissão para este usuário e tipo
        if user and permission_type:
            existing = Permission.objects.filter(
                user=user, 
                permission_type=permission_type
            ).exclude(id=self.instance.id if self.instance.id else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Já existe uma permissão do tipo "{dict(Permission.PERMISSION_CHOICES)[permission_type]}" '
                    f'para o usuário "{user.nome}".'
                )
        
        return cleaned_data


class RoleForm(forms.ModelForm):
    """Formulário para criação e edição de roles"""
    
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'name': 'Tipo de role no sistema',
            'description': 'Descrição detalhada das responsabilidades do role',
            'is_active': 'Role ativo no sistema',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Informações do Role',
                'name',
                'description',
                HTML('<div class="form-check mt-3">'),
                'is_active',
                HTML('</div>'),
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )


class UserRoleForm(forms.ModelForm):
    """Formulário para associação de usuários a roles"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(status=0),
        label='Usuário',
        help_text='Selecione o usuário para associar ao role',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        label='Role',
        help_text='Selecione o role a ser associado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserRole
        fields = ['user', 'role', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'is_active': 'Associação ativa',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Associação Usuário-Role',
                Row(
                    Column('user', css_class='form-group col-md-6 mb-0'),
                    Column('role', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                HTML('<div class="form-check mt-3">'),
                'is_active',
                HTML('</div>'),
            ),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        )
    
    def clean(self):
        """Validação customizada"""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        role = cleaned_data.get('role')
        
        # Verificar se já existe uma associação para este usuário e role
        if user and role:
            existing = UserRole.objects.filter(
                user=user, 
                role=role
            ).exclude(id=self.instance.id if self.instance.id else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'O usuário "{user.nome}" já possui o role "{role.get_name_display()}".'
                )
        
        return cleaned_data


class PermissionSearchForm(forms.Form):
    """Formulário de busca para permissões"""
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por usuário...',
            'class': 'form-control'
        })
    )
    
    permission_type = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Permission.PERMISSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    granted = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Concedidas'), ('false', 'Revogadas')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(status=0),
        required=False,
        empty_label='Todos os usuários',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-3 mb-0'),
                Column('permission_type', css_class='form-group col-md-3 mb-0'),
                Column('granted', css_class='form-group col-md-2 mb-0'),
                Column('user', css_class='form-group col-md-2 mb-0'),
                Column(
                    Submit('submit', 'Buscar', css_class='btn btn-outline-primary w-100'),
                    css_class='form-group col-md-2 mb-0'
                ),
                css_class='form-row'
            )
        )


class BulkPermissionForm(forms.Form):
    """Formulário para concessão em lote de permissões"""
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(status=0),
        widget=forms.CheckboxSelectMultiple,
        label='Usuários',
        help_text='Selecione os usuários que receberão as permissões'
    )
    
    permissions = forms.MultipleChoiceField(
        choices=Permission.PERMISSION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Permissões',
        help_text='Selecione as permissões a serem concedidas'
    )
    
    granted = forms.BooleanField(
        initial=True,
        required=False,
        label='Conceder permissões',
        help_text='Marque para conceder, desmarque para revogar'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Concessão em Lote',
                'users',
                'permissions',
                HTML('<div class="form-check mt-3">'),
                'granted',
                HTML('</div>'),
            ),
            FormActions(
                Submit('submit', 'Aplicar Permissões', css_class='btn btn-primary'),
                Button('cancel', 'Cancelar', css_class='btn btn-secondary', onclick='history.back()'),
            )
        ) 