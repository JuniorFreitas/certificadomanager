*** Settings ***
Documentation    Testes de integração end-to-end do sistema de certificados
Library          SeleniumLibrary
Library          RequestsLibrary
Library          DatabaseLibrary
Library          Collections
Library          String
Resource         ../../resources/keywords/common_keywords.robot
Resource         ../../resources/keywords/certificate_keywords.robot
Variables        ../../resources/variables/common_variables.robot
Suite Setup      Setup Integration Testing
Suite Teardown   Teardown Integration Testing
Test Setup       Test Setup
Test Teardown    Test Teardown

*** Variables ***
${RANDOM_SUFFIX}    ${EMPTY}
${DB_CONNECTION}    ${EMPTY}

*** Test Cases ***
Complete Certificate Lifecycle
    [Documentation]    Testa o ciclo completo de vida de um certificado
    [Tags]    integration    e2e    lifecycle
    ${cert_name}=    Set Variable    E2E_Lifecycle_${RANDOM_SUFFIX}
    ${domain}=    Set Variable    lifecycle.example.com
    
    # 1. Criar certificado via interface web
    Login As Admin
    Create New Certificate    ${cert_name}    ${domain}    SSL    90
    Verify Certificate Exists    ${cert_name}
    
    # 2. Verificar no banco de dados
    Verify Certificate In Database    ${cert_name}    ${domain}
    
    # 3. Verificar via API
    ${cert_id}=    Get Certificate ID From Database    ${cert_name}
    Verify Certificate Via API    ${cert_id}    ${cert_name}    ${domain}
    
    # 4. Editar certificado
    ${new_domain}=    Set Variable    updated-lifecycle.example.com
    Edit Certificate    ${cert_name}    ${cert_name}    ${new_domain}
    
    # 5. Verificar alteração no banco
    Verify Certificate In Database    ${cert_name}    ${new_domain}
    
    # 6. Monitorar status
    Verify Certificate Monitoring Alert    ${cert_name}
    
    # 7. Renovar certificado
    Renew Certificate    ${cert_name}
    
    # 8. Deletar certificado
    Delete Certificate    ${cert_name}
    Verify Certificate Not In Database    ${cert_name}

Multi-User Certificate Management
    [Documentation]    Testa gerenciamento de certificados com múltiplos usuários
    [Tags]    integration    e2e    multiuser
    ${admin_cert}=    Set Variable    Admin_Cert_${RANDOM_SUFFIX}
    ${user_cert}=    Set Variable    User_Cert_${RANDOM_SUFFIX}
    
    # Admin cria certificado
    Login As Admin
    Create New Certificate    ${admin_cert}    admin.example.com    SSL
    Logout User
    
    # Usuário regular tenta acessar
    Login As Regular User
    Navigate To Certificates Page
    ${can_see_admin_cert}=    Run Keyword And Return Status    Page Should Contain    ${admin_cert}
    Log    User can see admin certificate: ${can_see_admin_cert}
    
    # Usuário cria seu próprio certificado
    Create New Certificate    ${user_cert}    user.example.com    SSL
    Logout User
    
    # Admin verifica ambos certificados
    Login As Admin
    Verify Certificate Exists    ${admin_cert}
    Verify Certificate Exists    ${user_cert}
    
    # Limpeza
    Delete Certificate    ${admin_cert}
    Delete Certificate    ${user_cert}

Bulk Operations Workflow
    [Documentation]    Testa fluxo de trabalho com operações em lote
    [Tags]    integration    e2e    bulk
    ${cert_prefix}=    Set Variable    Bulk_E2E_${RANDOM_SUFFIX}
    @{cert_names}=    Create List
    
    # Criar múltiplos certificados
    Login As Admin
    FOR    ${i}    IN RANGE    5
        ${cert_name}=    Set Variable    ${cert_prefix}_${i}
        ${domain}=    Set Variable    bulk${i}.example.com
        Create New Certificate    ${cert_name}    ${domain}    SSL
        Append To List    ${cert_names}    ${cert_name}
    END
    
    # Verificar todos no banco
    FOR    ${cert_name}    IN    @{cert_names}
        Verify Certificate In Database    ${cert_name}    bulk*.example.com
    END
    
    # Exportar lista
    Export Certificates List    CSV
    
    # Deletar em lote
    Bulk Delete Certificates    @{cert_names}
    
    # Verificar remoção do banco
    FOR    ${cert_name}    IN    @{cert_names}
        Verify Certificate Not In Database    ${cert_name}
    END

Certificate Monitoring Integration
    [Documentation]    Testa integração com sistema de monitoramento
    [Tags]    integration    e2e    monitoring
    ${cert_name}=    Set Variable    Monitoring_E2E_${RANDOM_SUFFIX}
    
    # Criar certificado próximo ao vencimento
    Login As Admin
    Create New Certificate    ${cert_name}    monitoring.example.com    SSL    5
    
    # Verificar aparece no monitoramento
    Navigate To Page    /monitoring/
    Page Should Contain    ${cert_name}
    
    # Verificar via API de monitoramento
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    GET    ${API_BASE_URL}/monitoring/expiring/    headers=${headers}
    Should Contain    ${response.text}    ${cert_name}
    
    # Renovar e verificar que sai do monitoramento
    Navigate To Certificates Page
    Renew Certificate    ${cert_name}
    Navigate To Page    /monitoring/
    ${still_monitored}=    Run Keyword And Return Status    Page Should Contain    ${cert_name}
    Should Be False    ${still_monitored}
    
    # Limpeza
    Navigate To Certificates Page
    Delete Certificate    ${cert_name}

API and Web Consistency
    [Documentation]    Testa consistência entre API e interface web
    [Tags]    integration    e2e    consistency
    ${cert_name}=    Set Variable    Consistency_E2E_${RANDOM_SUFFIX}
    ${domain}=    Set Variable    consistency.example.com
    
    # Criar via API
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${data}=    Create Dictionary    
    ...    name=${cert_name}
    ...    domain=${domain}
    ...    type=SSL
    ...    expiry_days=90
    ${response}=    POST    ${API_BASE_URL}/certificates/    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    201
    ${cert_id}=    Set Variable    ${response.json()}[id]
    
    # Verificar na interface web
    Login As Admin
    Verify Certificate Exists    ${cert_name}
    Verify Certificate Details    ${cert_name}    ${domain}    SSL
    
    # Editar via web
    ${new_domain}=    Set Variable    updated-consistency.example.com
    Edit Certificate    ${cert_name}    ${cert_name}    ${new_domain}
    
    # Verificar via API
    ${response}=    GET    ${API_BASE_URL}/certificates/${cert_id}/    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Should Be Equal As Strings    ${response.json()}[domain]    ${new_domain}
    
    # Deletar via API
    ${response}=    DELETE    ${API_BASE_URL}/certificates/${cert_id}/    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    
    # Verificar na web
    Verify Certificate Does Not Exist    ${cert_name}

Permission System Integration
    [Documentation]    Testa integração com sistema de permissões
    [Tags]    integration    e2e    permissions
    ${cert_name}=    Set Variable    Permission_E2E_${RANDOM_SUFFIX}
    
    # Admin cria certificado
    Login As Admin
    Create New Certificate    ${cert_name}    permission.example.com    SSL
    
    # Verificar permissões no banco
    ${admin_permissions}=    Query Database    
    ...    SELECT p.name FROM auth_user_user_permissions uup 
    ...    JOIN auth_permission p ON uup.permission_id = p.id 
    ...    JOIN auth_user u ON uup.user_id = u.id 
    ...    WHERE u.username = '${ADMIN_USERNAME}'
    Log    Admin permissions: ${admin_permissions}
    
    Logout User
    
    # Usuário regular tenta acessar
    Login As Regular User
    Navigate To Certificates Page
    ${can_create}=    Run Keyword And Return Status    
    ...    Page Should Contain Element    xpath=//a[contains(text(), 'Add') or contains(text(), 'Create')]
    Log    Regular user can create certificates: ${can_create}
    
    # Limpeza
    Logout User
    Login As Admin
    Delete Certificate    ${cert_name}

Database Backup and Restore Simulation
    [Documentation]    Simula backup e restore de dados de certificados
    [Tags]    integration    e2e    backup    slow
    ${cert_name}=    Set Variable    Backup_E2E_${RANDOM_SUFFIX}
    
    # Criar certificado
    Login As Admin
    Create New Certificate    ${cert_name}    backup.example.com    SSL
    
    # "Backup" - obter dados do banco
    ${original_data}=    Query Database    
    ...    SELECT name, domain, type FROM certificates_certificate WHERE name = '${cert_name}'
    
    # Simular perda/corrupção (deletar)
    Execute SQL String    DELETE FROM certificates_certificate WHERE name = '${cert_name}'
    
    # Verificar que não existe mais
    Navigate To Certificates Page
    Verify Certificate Does Not Exist    ${cert_name}
    
    # "Restore" - recriar com dados do backup
    ${name}=    Set Variable    ${original_data[0][0]}
    ${domain}=    Set Variable    ${original_data[0][1]}
    ${type}=    Set Variable    ${original_data[0][2]}
    Create New Certificate    ${name}    ${domain}    ${type}
    
    # Verificar restore
    Verify Certificate Exists    ${cert_name}
    
    # Limpeza
    Delete Certificate    ${cert_name}

Performance Under Load
    [Documentation]    Testa performance do sistema sob carga
    [Tags]    integration    e2e    performance    slow
    ${cert_prefix}=    Set Variable    Load_E2E_${RANDOM_SUFFIX}
    
    # Criar muitos certificados rapidamente
    Login As Admin
    ${start_time}=    Get Current Date    result_format=epoch
    
    FOR    ${i}    IN RANGE    20
        ${cert_name}=    Set Variable    ${cert_prefix}_${i}
        Create New Certificate    ${cert_name}    load${i}.example.com    SSL
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    Log    Time to create 20 certificates: ${duration} seconds
    
    # Testar listagem com muitos certificados
    Navigate To Certificates Page
    ${list_start}=    Get Current Date    result_format=epoch
    Wait Until Page Contains Element    class=certificate-list
    ${list_end}=    Get Current Date    result_format=epoch
    ${list_duration}=    Evaluate    ${list_end} - ${list_start}
    Log    Time to load certificate list: ${list_duration} seconds
    
    # Limpeza
    FOR    ${i}    IN RANGE    20
        ${cert_name}=    Set Variable    ${cert_prefix}_${i}
        Delete Certificate    ${cert_name}
    END

*** Keywords ***
Setup Integration Testing
    [Documentation]    Configuração inicial para testes de integração
    Setup Browser
    ${timestamp}=    Get Current Timestamp
    Set Suite Variable    ${RANDOM_SUFFIX}    ${timestamp}
    
    # Configurar conexão com banco de dados
    Connect To Database Using Custom Params    
    ...    dbapiModuleName=sqlite3
    ...    dbConfigFile=../../../db.sqlite3

Teardown Integration Testing
    [Documentation]    Limpeza final dos testes de integração
    Disconnect From Database
    Teardown Browser

Test Setup
    [Documentation]    Setup para cada teste
    # Pode incluir limpeza de dados de teste anteriores
    Log    Starting integration test

Test Teardown
    [Documentation]    Teardown para cada teste
    Take Screenshot On Failure
    Run Keyword If Test Failed    Log Database State
    # Cleanup específico pode ser adicionado aqui

Verify Certificate In Database
    [Documentation]    Verifica se certificado existe no banco de dados
    [Arguments]    ${cert_name}    ${domain}
    ${result}=    Query Database    
    ...    SELECT name, domain FROM certificates_certificate 
    ...    WHERE name = '${cert_name}' AND domain LIKE '${domain}'
    Should Not Be Empty    ${result}
    Should Be Equal As Strings    ${result[0][0]}    ${cert_name}

Verify Certificate Not In Database
    [Documentation]    Verifica se certificado não existe no banco de dados
    [Arguments]    ${cert_name}
    ${result}=    Query Database    
    ...    SELECT name FROM certificates_certificate WHERE name = '${cert_name}'
    Should Be Empty    ${result}

Get Certificate ID From Database
    [Documentation]    Obtém ID do certificado no banco de dados
    [Arguments]    ${cert_name}
    ${result}=    Query Database    
    ...    SELECT id FROM certificates_certificate WHERE name = '${cert_name}'
    Should Not Be Empty    ${result}
    [Return]    ${result[0][0]}

Verify Certificate Via API
    [Documentation]    Verifica certificado via API
    [Arguments]    ${cert_id}    ${cert_name}    ${domain}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    GET    ${API_BASE_URL}/certificates/${cert_id}/    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Should Be Equal As Strings    ${response.json()}[name]    ${cert_name}
    Should Be Equal As Strings    ${response.json()}[domain]    ${domain}

Log Database State
    [Documentation]    Registra estado atual do banco de dados para debug
    ${count}=    Query Database    SELECT COUNT(*) FROM certificates_certificate
    Log    Current certificate count in database: ${count[0][0]} 