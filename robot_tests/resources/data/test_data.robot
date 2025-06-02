*** Variables ***
# Dados de teste para certificados
@{VALID_DOMAINS}    example.com    test.domain.com    secure.site.org    my-app.net
@{INVALID_DOMAINS}    invalid-domain    .com    domain.    -invalid.com    domain..com

@{CERTIFICATE_TYPES}    SSL    TLS    Code Signing    Email    Root CA

@{TEST_USERS}    
...    testuser1:test1@example.com:password123
...    testuser2:test2@example.com:password456
...    testuser3:test3@example.com:password789

# Dados para testes de performance
${BULK_CERT_COUNT}    50
${LOAD_TEST_USERS}    10

# Dados para testes de segurança
@{SQL_INJECTION_PAYLOADS}    
...    ' OR '1'='1
...    '; DROP TABLE certificates; --
...    ' UNION SELECT * FROM users --
...    <script>alert('xss')</script>

@{XSS_PAYLOADS}
...    <script>alert('XSS')</script>
...    javascript:alert('XSS')
...    <img src=x onerror=alert('XSS')>
...    "><script>alert('XSS')</script>

# Configurações de teste
&{TEST_CONFIG}
...    max_wait_time=30
...    retry_count=3
...    screenshot_on_failure=True
...    cleanup_after_test=True

# Dados de certificados para diferentes cenários
&{VALID_CERTIFICATE}
...    name=Valid Test Certificate
...    domain=valid.example.com
...    type=SSL
...    expiry_days=90
...    organization=Test Organization
...    country=US

&{EXPIRING_CERTIFICATE}
...    name=Expiring Test Certificate
...    domain=expiring.example.com
...    type=SSL
...    expiry_days=5
...    organization=Test Organization
...    country=US

&{EXPIRED_CERTIFICATE}
...    name=Expired Test Certificate
...    domain=expired.example.com
...    type=SSL
...    expiry_days=-10
...    organization=Test Organization
...    country=US

# Dados de usuários para diferentes cenários
&{ADMIN_USER}
...    username=admin_test
...    email=admin@test.com
...    password=admin123
...    first_name=Admin
...    last_name=User
...    is_staff=True
...    is_superuser=True

&{REGULAR_USER}
...    username=regular_test
...    email=regular@test.com
...    password=user123
...    first_name=Regular
...    last_name=User
...    is_staff=False
...    is_superuser=False

&{MANAGER_USER}
...    username=manager_test
...    email=manager@test.com
...    password=manager123
...    first_name=Manager
...    last_name=User
...    is_staff=True
...    is_superuser=False

# Mensagens de erro esperadas
&{ERROR_MESSAGES}
...    required_field=This field is required
...    invalid_email=Enter a valid email address
...    password_mismatch=Passwords do not match
...    duplicate_username=User with this username already exists
...    invalid_domain=Enter a valid domain name
...    certificate_exists=Certificate with this name already exists
...    permission_denied=You do not have permission to perform this action
...    login_required=Please log in to continue

# URLs da aplicação
&{APP_URLS}
...    login=/login/
...    logout=/logout/
...    dashboard=/
...    certificates=/certificates/
...    users=/users/
...    monitoring=/monitoring/
...    permissions=/permissions/
...    accounts=/accounts/
...    resources=/resources/

# Seletores CSS/XPath comuns
&{SELECTORS}
...    login_form=form#login-form
...    username_field=input#id_username
...    password_field=input#id_password
...    submit_button=button[type="submit"]
...    error_message=.alert-danger
...    success_message=.alert-success
...    loading_spinner=.spinner
...    modal_dialog=.modal
...    data_table=table.data-table
...    pagination=.pagination
...    search_field=input[name="search"]
...    filter_dropdown=select.filter 