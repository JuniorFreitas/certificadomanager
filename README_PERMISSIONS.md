# Módulo de Permissões - FCM

## Visão Geral

O módulo de permissões do FCM (Finnet Certificate Manager) implementa um sistema completo de controle de acesso baseado em roles e permissões granulares, conforme especificado no PRD.

## Funcionalidades Implementadas

### 1. Sistema de Roles
- **4 Roles Predefinidos:**
  - **Administrador**: Acesso total ao sistema
  - **Gerente**: Supervisão e relatórios gerenciais
  - **Usuário**: Operações do dia a dia
  - **Visualizador**: Acesso somente leitura

### 2. Permissões Granulares
- **20 Tipos de Permissões** organizadas por módulo:
  - **Usuários**: view, create, edit, delete
  - **Certificados**: view, create, edit, delete
  - **Contas**: view, create, edit, delete
  - **Recursos**: view, create, edit, delete
  - **Permissões**: view, create, edit, delete

### 3. Associações Usuário-Role
- Sistema flexível que permite múltiplos roles por usuário
- Controle de status (ativo/inativo)
- Auditoria completa de criação e alterações

## Estrutura do Módulo

```
apps/permissions/
├── models.py          # Modelos Role, Permission, UserRole
├── views.py           # Views completas para CRUD
├── forms.py           # Formulários com validação
├── urls.py            # URLs do módulo
├── admin.py           # Interface administrativa
└── tests.py           # Testes unitários

templates/permissions/
├── dashboard.html                    # Dashboard principal
├── permission_list.html             # Lista de permissões
├── permission_form.html             # Formulário de permissões
├── permission_confirm_delete.html   # Confirmação de exclusão
├── role_list.html                   # Lista de roles
├── role_form.html                   # Formulário de roles
├── role_detail.html                 # Detalhes do role
├── role_confirm_delete.html         # Confirmação de exclusão
├── user_role_list.html              # Lista de associações
├── user_role_form.html              # Formulário de associações
├── user_role_confirm_delete.html    # Confirmação de exclusão
├── bulk_permissions.html            # Atribuição em massa
└── permission_report.html           # Relatório com gráficos
```

## Modelos de Dados

### Role
```python
- id (CharField, PK)
- name (CharField, choices)
- description (TextField)
- is_active (BooleanField)
- data_cad, usu_cad, data_atu, usu_atu (Auditoria)
```

### Permission
```python
- id (CharField, PK)
- user (ForeignKey User)
- permission_type (CharField, choices)
- granted (BooleanField)
- data_cad, usu_cad, data_atu, usu_atu (Auditoria)
```

### UserRole
```python
- id (CharField, PK)
- user (ForeignKey User)
- role (ForeignKey Role)
- is_active (BooleanField)
- data_cad, usu_cad, data_atu, usu_atu (Auditoria)
```

## Views Implementadas

### Dashboard
- **URL**: `/permissions/`
- **Funcionalidade**: Visão geral com estatísticas e gráficos
- **Recursos**: Cards informativos, gráficos Chart.js, ações rápidas

### Permissões
- **Lista**: `/permissions/permissions/` - Listagem com busca e filtros
- **Criar**: `/permissions/permissions/create/` - Formulário de criação
- **Editar**: `/permissions/permissions/<id>/edit/` - Edição
- **Excluir**: `/permissions/permissions/<id>/delete/` - Confirmação
- **Relatório**: `/permissions/report/` - Relatório com gráficos

### Roles
- **Lista**: `/permissions/roles/` - Listagem com estatísticas
- **Criar**: `/permissions/roles/create/` - Formulário de criação
- **Detalhe**: `/permissions/roles/<id>/` - Visualização detalhada
- **Editar**: `/permissions/roles/<id>/edit/` - Edição
- **Excluir**: `/permissions/roles/<id>/delete/` - Confirmação

### Associações Usuário-Role
- **Lista**: `/permissions/user-roles/` - Listagem com filtros
- **Criar**: `/permissions/user-roles/create/` - Nova associação
- **Editar**: `/permissions/user-roles/<id>/edit/` - Edição
- **Excluir**: `/permissions/user-roles/<id>/delete/` - Confirmação

### Funcionalidades Especiais
- **Atribuição em Massa**: `/permissions/bulk/` - Múltiplas permissões
- **Relatório**: `/permissions/report/` - Estatísticas e gráficos

## Formulários

### PermissionForm
- Seleção de usuário e tipo de permissão
- Validação de duplicatas
- Campo de status (concedida/negada)

### RoleForm
- Criação/edição de roles
- Validação de nome único
- Campo de descrição

### UserRoleForm
- Associação usuário-role
- Validação de duplicatas
- Controle de status

### BulkPermissionForm
- Seleção múltipla de usuários
- Seleção múltipla de permissões
- Ação (conceder/revogar)

## Interface do Usuário

### Design
- **Bootstrap 5** para responsividade
- **FontAwesome** para ícones
- **Chart.js** para gráficos
- **Crispy Forms** para formulários elegantes

### Recursos de UX
- Busca em tempo real
- Filtros avançados
- Paginação
- Mensagens de feedback
- Confirmações de ações críticas
- Tooltips informativos

### Navegação
- Menu dropdown no navbar principal
- Breadcrumbs em páginas internas
- Botões de ação contextuais
- Links de navegação rápida

## Segurança

### Validações
- Verificação de duplicatas
- Validação de campos obrigatórios
- Sanitização de entrada
- Proteção CSRF

### Auditoria
- Registro de criação (data_cad, usu_cad)
- Registro de atualização (data_atu, usu_atu)
- Histórico de alterações
- Rastreabilidade completa

## Dados de Demonstração

O script `create_permissions_data.py` cria:
- 4 roles predefinidos
- 20 permissões para o usuário admin
- 1 associação usuário-role
- Dados realistas para demonstração

## Testes

### Cobertura
- Testes de modelos
- Testes de views
- Testes de formulários
- Validação de constraints

### Execução
```bash
python manage.py test apps.permissions
```

## URLs Principais

```
/permissions/                          # Dashboard
/permissions/permissions/              # Lista de permissões
/permissions/permissions/create/       # Criar permissão
/permissions/roles/                    # Lista de roles
/permissions/roles/create/             # Criar role
/permissions/user-roles/               # Associações usuário-role
/permissions/user-roles/create/        # Nova associação
/permissions/bulk/                     # Atribuição em massa
/permissions/report/                   # Relatório
```

## Próximos Passos

1. **Integração com Middleware**: Implementar middleware de verificação de permissões
2. **API REST**: Endpoints para integração externa
3. **Logs Avançados**: Sistema de auditoria mais detalhado
4. **Notificações**: Alertas de mudanças de permissões
5. **Importação/Exportação**: Backup e restore de configurações

## Tecnologias Utilizadas

- **Django 4.2**: Framework principal
- **PostgreSQL**: Banco de dados
- **Bootstrap 5**: Framework CSS
- **Chart.js**: Gráficos interativos
- **FontAwesome**: Ícones
- **Crispy Forms**: Formulários elegantes

## Status

✅ **Módulo Completo e Funcional**
- Todos os CRUDs implementados
- Interface moderna e responsiva
- Dados de demonstração criados
- Testes passando
- Documentação completa

O módulo de permissões está pronto para uso em produção e pode ser facilmente estendido conforme necessidades futuras. 