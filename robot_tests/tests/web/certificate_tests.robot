*** Settings ***
Documentation    Testes de gerenciamento de certificados
Library          SeleniumLibrary
Library          String
Resource         ../../resources/keywords/common_keywords.robot
Resource         ../../resources/keywords/certificate_keywords.robot
Variables        ../../resources/variables/common_variables.robot
Suite Setup      Test Suite Setup
Suite Teardown   Test Suite Teardown
Test Setup       Login As Admin
Test Teardown    Test Teardown

*** Variables ***
${RANDOM_SUFFIX}    ${EMPTY}

*** Test Cases ***
Create New Certificate
    [Documentation]    Testa criação de um novo certificado
    [Tags]    smoke    certificates    create
    ${cert_name}=    Set Variable    ${TEST_CERT_NAME}_${RANDOM_SUFFIX}
    Create New Certificate    ${cert_name}    ${TEST_CERT_DOMAIN}    ${TEST_CERT_TYPE}
    Verify Certificate Exists    ${cert_name}

Create Certificate With Special Characters
    [Documentation]    Testa criação de certificado com caracteres especiais
    [Tags]    regression    certificates    create
    ${cert_name}=    Set Variable    Test-Cert_${RANDOM_SUFFIX}@domain.com
    Create New Certificate    ${cert_name}    sub.test-domain.com    SSL
    Verify Certificate Exists    ${cert_name}

Create Certificate With Long Name
    [Documentation]    Testa criação de certificado com nome longo
    [Tags]    regression    certificates    create
    ${long_name}=    Generate Random String    100
    ${cert_name}=    Set Variable    ${long_name}_${RANDOM_SUFFIX}
    Create New Certificate    ${cert_name}    longdomain.example.com    SSL
    Verify Certificate Exists    ${cert_name}

Edit Certificate Details
    [Documentation]    Testa edição de detalhes de certificado existente
    [Tags]    smoke    certificates    edit
    ${cert_name}=    Set Variable    EditTest_${RANDOM_SUFFIX}
    ${new_name}=    Set Variable    EditedCert_${RANDOM_SUFFIX}
    ${new_domain}=    Set Variable    edited.example.com
    
    Create New Certificate    ${cert_name}    original.example.com    SSL
    Edit Certificate    ${cert_name}    ${new_name}    ${new_domain}
    Verify Certificate Exists    ${new_name}
    Verify Certificate Does Not Exist    ${cert_name}

Delete Single Certificate
    [Documentation]    Testa remoção de um certificado individual
    [Tags]    smoke    certificates    delete
    ${cert_name}=    Set Variable    DeleteTest_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert_name}    delete.example.com    SSL
    Verify Certificate Exists    ${cert_name}
    Delete Certificate    ${cert_name}
    Verify Certificate Does Not Exist    ${cert_name}

Bulk Delete Certificates
    [Documentation]    Testa remoção em lote de certificados
    [Tags]    regression    certificates    delete    bulk
    ${cert1}=    Set Variable    BulkDelete1_${RANDOM_SUFFIX}
    ${cert2}=    Set Variable    BulkDelete2_${RANDOM_SUFFIX}
    ${cert3}=    Set Variable    BulkDelete3_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert1}    bulk1.example.com    SSL
    Create New Certificate    ${cert2}    bulk2.example.com    SSL
    Create New Certificate    ${cert3}    bulk3.example.com    SSL
    
    Bulk Delete Certificates    ${cert1}    ${cert2}    ${cert3}
    
    Verify Certificate Does Not Exist    ${cert1}
    Verify Certificate Does Not Exist    ${cert2}
    Verify Certificate Does Not Exist    ${cert3}

Search Certificate By Name
    [Documentation]    Testa busca de certificados por nome
    [Tags]    smoke    certificates    search
    ${cert_name}=    Set Variable    SearchTest_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert_name}    search.example.com    SSL
    Search Certificate    ${cert_name}
    Page Should Contain    ${cert_name}

Search Certificate By Domain
    [Documentation]    Testa busca de certificados por domínio
    [Tags]    regression    certificates    search
    ${cert_name}=    Set Variable    DomainSearch_${RANDOM_SUFFIX}
    ${domain}=    Set Variable    searchdomain_${RANDOM_SUFFIX}.com
    
    Create New Certificate    ${cert_name}    ${domain}    SSL
    Search Certificate    ${domain}
    Page Should Contain    ${cert_name}
    Page Should Contain    ${domain}

Filter Certificates By Status
    [Documentation]    Testa filtro de certificados por status
    [Tags]    regression    certificates    filter
    Filter Certificates By Status    Active
    Page Should Contain Element    class=filtered-results

View Certificate Details
    [Documentation]    Testa visualização de detalhes de certificado
    [Tags]    smoke    certificates    view
    ${cert_name}=    Set Variable    DetailsTest_${RANDOM_SUFFIX}
    ${domain}=    Set Variable    details.example.com
    
    Create New Certificate    ${cert_name}    ${domain}    SSL
    Verify Certificate Details    ${cert_name}    ${domain}    SSL

Check Expiry Warning
    [Documentation]    Testa verificação de aviso de expiração
    [Tags]    regression    certificates    monitoring
    ${cert_name}=    Set Variable    ExpiryTest_${RANDOM_SUFFIX}
    
    # Cria certificado com poucos dias para expirar
    Create New Certificate    ${cert_name}    expiry.example.com    SSL    5
    ${warning_present}=    Check Certificate Expiry Warning    ${cert_name}
    Log    Expiry warning present: ${warning_present}

Export Certificates List
    [Documentation]    Testa exportação da lista de certificados
    [Tags]    regression    certificates    export
    ${cert_name}=    Set Variable    ExportTest_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert_name}    export.example.com    SSL
    Export Certificates List    CSV

Renew Certificate
    [Documentation]    Testa renovação de certificado
    [Tags]    regression    certificates    renew
    ${cert_name}=    Set Variable    RenewTest_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert_name}    renew.example.com    SSL
    Renew Certificate    ${cert_name}

Create Certificate With Invalid Data
    [Documentation]    Testa criação de certificado com dados inválidos
    [Tags]    regression    certificates    negative
    Navigate To Certificates Page
    Click Link    xpath=//a[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]
    
    # Tenta criar sem nome
    Input Text    id=id_domain    invalid.example.com
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Page Should Contain Element    css=.error, .invalid-feedback
    
    # Tenta criar com domínio inválido
    Navigate To Certificates Page
    Click Link    xpath=//a[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]
    Input Text    id=id_name    InvalidDomain_${RANDOM_SUFFIX}
    Input Text    id=id_domain    invalid-domain
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Page Should Contain Element    css=.error, .invalid-feedback

Create Duplicate Certificate
    [Documentation]    Testa criação de certificado duplicado
    [Tags]    regression    certificates    negative
    ${cert_name}=    Set Variable    DuplicateTest_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert_name}    duplicate.example.com    SSL
    
    # Tenta criar certificado com mesmo nome
    Navigate To Certificates Page
    Click Link    xpath=//a[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]
    Input Text    id=id_name    ${cert_name}
    Input Text    id=id_domain    duplicate2.example.com
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Page Should Contain    already exists

Certificate Pagination
    [Documentation]    Testa paginação da lista de certificados
    [Tags]    regression    certificates    pagination
    Navigate To Certificates Page
    ${pagination_exists}=    Run Keyword And Return Status    Page Should Contain Element    class=pagination
    Run Keyword If    ${pagination_exists}    Test Pagination Functionality

Certificate Sorting
    [Documentation]    Testa ordenação da lista de certificados
    [Tags]    regression    certificates    sorting
    Navigate To Certificates Page
    ${sort_exists}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//th[contains(@class, 'sortable')]
    Run Keyword If    ${sort_exists}    Test Sorting Functionality

Certificate Monitoring Integration
    [Documentation]    Testa integração com sistema de monitoramento
    [Tags]    integration    certificates    monitoring
    ${cert_name}=    Set Variable    MonitoringTest_${RANDOM_SUFFIX}
    
    Create New Certificate    ${cert_name}    monitoring.example.com    SSL    10
    ${alert_present}=    Verify Certificate Monitoring Alert    ${cert_name}
    Log    Monitoring alert present: ${alert_present}

*** Keywords ***
Test Suite Setup
    [Documentation]    Configuração inicial da suíte de testes
    Setup Browser
    ${timestamp}=    Get Current Timestamp
    Set Suite Variable    ${RANDOM_SUFFIX}    ${timestamp}

Test Suite Teardown
    [Documentation]    Limpeza final da suíte de testes
    Teardown Browser

Test Teardown
    [Documentation]    Limpeza após cada teste
    Take Screenshot On Failure
    Logout User

Test Pagination Functionality
    [Documentation]    Testa funcionalidade de paginação
    Click Link    xpath=//a[contains(@class, 'page-link') and text()='2']
    Wait Until Page Contains Element    class=pagination
    Page Should Contain Element    xpath=//a[contains(@class, 'page-link') and text()='1']

Test Sorting Functionality
    [Documentation]    Testa funcionalidade de ordenação
    Click Element    xpath=//th[contains(@class, 'sortable')][1]
    Wait Until Page Contains Element    class=sorted
    Click Element    xpath=//th[contains(@class, 'sortable')][1]
    Wait Until Page Contains Element    class=sorted 