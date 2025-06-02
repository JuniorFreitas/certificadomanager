*** Settings ***
Documentation    Testes de API para gerenciamento de certificados
Library          RequestsLibrary
Library          Collections
Library          String
Library          DateTime
Resource         ../../resources/keywords/common_keywords.robot
Variables        ../../resources/variables/common_variables.robot
Suite Setup      Setup API Testing
Suite Teardown   Teardown API Testing
Test Setup       Create Session    certificateapi    ${API_BASE_URL}
Test Teardown    Delete All Sessions

*** Variables ***
${AUTH_TOKEN}       ${EMPTY}
${TEST_CERT_ID}     ${EMPTY}
${RANDOM_SUFFIX}    ${EMPTY}

*** Test Cases ***
GET All Certificates
    [Documentation]    Testa listagem de todos os certificados via API
    [Tags]    smoke    api    certificates    get
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}
    Verify API Response Status    ${response}    200
    Should Be Equal As Strings    ${response.headers['Content-Type']}    application/json
    ${json_data}=    Set Variable    ${response.json()}
    Should Be True    isinstance($json_data, list)

POST Create New Certificate
    [Documentation]    Testa criação de novo certificado via API
    [Tags]    smoke    api    certificates    post
    ${cert_name}=    Set Variable    API_Test_${RANDOM_SUFFIX}
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${data}=    Create Dictionary    
    ...    name=${cert_name}
    ...    domain=api-test.example.com
    ...    type=SSL
    ...    expiry_days=90
    
    ${response}=    POST On Session    certificateapi    /certificates/    json=${data}    headers=${headers}
    Verify API Response Status    ${response}    201
    ${json_data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json_data}    id
    Dictionary Should Contain Key    ${json_data}    name
    Should Be Equal As Strings    ${json_data}[name]    ${cert_name}
    Set Test Variable    ${TEST_CERT_ID}    ${json_data}[id]

GET Single Certificate
    [Documentation]    Testa obtenção de certificado específico via API
    [Tags]    smoke    api    certificates    get
    [Setup]    Create Test Certificate Via API
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    GET On Session    certificateapi    /certificates/${TEST_CERT_ID}/    headers=${headers}
    Verify API Response Status    ${response}    200
    ${json_data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json_data}    id
    Dictionary Should Contain Key    ${json_data}    name
    Dictionary Should Contain Key    ${json_data}    domain
    Should Be Equal As Strings    ${json_data}[id]    ${TEST_CERT_ID}

PUT Update Certificate
    [Documentation]    Testa atualização de certificado via API
    [Tags]    smoke    api    certificates    put
    [Setup]    Create Test Certificate Via API
    ${updated_name}=    Set Variable    Updated_API_Test_${RANDOM_SUFFIX}
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${data}=    Create Dictionary    
    ...    name=${updated_name}
    ...    domain=updated-api-test.example.com
    ...    type=SSL
    ...    expiry_days=120
    
    ${response}=    PUT On Session    certificateapi    /certificates/${TEST_CERT_ID}/    json=${data}    headers=${headers}
    Verify API Response Status    ${response}    200
    ${json_data}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${json_data}[name]    ${updated_name}
    Should Be Equal As Strings    ${json_data}[domain]    updated-api-test.example.com

PATCH Partial Update Certificate
    [Documentation]    Testa atualização parcial de certificado via API
    [Tags]    regression    api    certificates    patch
    [Setup]    Create Test Certificate Via API
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${data}=    Create Dictionary    domain=patched-domain.example.com
    
    ${response}=    PATCH On Session    certificateapi    /certificates/${TEST_CERT_ID}/    json=${data}    headers=${headers}
    Verify API Response Status    ${response}    200
    ${json_data}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${json_data}[domain]    patched-domain.example.com

DELETE Certificate
    [Documentation]    Testa remoção de certificado via API
    [Tags]    smoke    api    certificates    delete
    [Setup]    Create Test Certificate Via API
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    DELETE On Session    certificateapi    /certificates/${TEST_CERT_ID}/    headers=${headers}
    Verify API Response Status    ${response}    204
    
    # Verifica se foi realmente removido
    ${response}=    GET On Session    certificateapi    /certificates/${TEST_CERT_ID}/    headers=${headers}    expected_status=404

POST Create Certificate With Invalid Data
    [Documentation]    Testa criação de certificado com dados inválidos
    [Tags]    regression    api    certificates    negative
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    
    # Testa sem nome obrigatório
    ${data}=    Create Dictionary    domain=invalid.example.com    type=SSL
    ${response}=    POST On Session    certificateapi    /certificates/    json=${data}    headers=${headers}    expected_status=400
    
    # Testa com domínio inválido
    ${data}=    Create Dictionary    name=InvalidDomain    domain=invalid-domain    type=SSL
    ${response}=    POST On Session    certificateapi    /certificates/    json=${data}    headers=${headers}    expected_status=400

GET Certificate With Invalid ID
    [Documentation]    Testa obtenção de certificado com ID inválido
    [Tags]    regression    api    certificates    negative
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    GET On Session    certificateapi    /certificates/99999/    headers=${headers}    expected_status=404

PUT Update Nonexistent Certificate
    [Documentation]    Testa atualização de certificado inexistente
    [Tags]    regression    api    certificates    negative
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${data}=    Create Dictionary    name=Nonexistent    domain=test.com    type=SSL
    ${response}=    PUT On Session    certificateapi    /certificates/99999/    json=${data}    headers=${headers}    expected_status=404

DELETE Nonexistent Certificate
    [Documentation]    Testa remoção de certificado inexistente
    [Tags]    regression    api    certificates    negative
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    DELETE On Session    certificateapi    /certificates/99999/    headers=${headers}    expected_status=404

GET Certificates With Pagination
    [Documentation]    Testa paginação na listagem de certificados
    [Tags]    regression    api    certificates    pagination
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${params}=    Create Dictionary    page=1    limit=10
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}    params=${params}
    Verify API Response Status    ${response}    200
    ${json_data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json_data}    results
    Dictionary Should Contain Key    ${json_data}    count
    Dictionary Should Contain Key    ${json_data}    next
    Dictionary Should Contain Key    ${json_data}    previous

GET Certificates With Filtering
    [Documentation]    Testa filtros na listagem de certificados
    [Tags]    regression    api    certificates    filter
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${params}=    Create Dictionary    type=SSL    status=active
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}    params=${params}
    Verify API Response Status    ${response}    200
    ${json_data}=    Set Variable    ${response.json()}
    Should Be True    isinstance($json_data, list) or isinstance($json_data.get('results'), list)

GET Certificates With Search
    [Documentation]    Testa busca na listagem de certificados
    [Tags]    regression    api    certificates    search
    [Setup]    Create Test Certificate Via API
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${params}=    Create Dictionary    search=API_Test
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}    params=${params}
    Verify API Response Status    ${response}    200

GET Certificates With Sorting
    [Documentation]    Testa ordenação na listagem de certificados
    [Tags]    regression    api    certificates    sorting
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${params}=    Create Dictionary    ordering=name
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}    params=${params}
    Verify API Response Status    ${response}    200
    
    ${params}=    Create Dictionary    ordering=-created_at
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}    params=${params}
    Verify API Response Status    ${response}    200

POST Bulk Create Certificates
    [Documentation]    Testa criação em lote de certificados
    [Tags]    regression    api    certificates    bulk
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${certificates}=    Create List
    FOR    ${i}    IN RANGE    3
        ${cert_data}=    Create Dictionary    
        ...    name=Bulk_Test_${i}_${RANDOM_SUFFIX}
        ...    domain=bulk${i}.example.com
        ...    type=SSL
        ...    expiry_days=90
        Append To List    ${certificates}    ${cert_data}
    END
    
    ${data}=    Create Dictionary    certificates=${certificates}
    ${response}=    POST On Session    certificateapi    /certificates/bulk/    json=${data}    headers=${headers}
    Verify API Response Status    ${response}    201

GET Certificate Statistics
    [Documentation]    Testa obtenção de estatísticas de certificados
    [Tags]    regression    api    certificates    stats
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    GET On Session    certificateapi    /certificates/stats/    headers=${headers}
    Verify API Response Status    ${response}    200
    ${json_data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json_data}    total
    Dictionary Should Contain Key    ${json_data}    active
    Dictionary Should Contain Key    ${json_data}    expired
    Dictionary Should Contain Key    ${json_data}    expiring_soon

GET Expiring Certificates
    [Documentation]    Testa obtenção de certificados próximos ao vencimento
    [Tags]    regression    api    certificates    monitoring
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${params}=    Create Dictionary    days=30
    ${response}=    GET On Session    certificateapi    /certificates/expiring/    headers=${headers}    params=${params}
    Verify API Response Status    ${response}    200

POST Renew Certificate
    [Documentation]    Testa renovação de certificado via API
    [Tags]    regression    api    certificates    renew
    [Setup]    Create Test Certificate Via API
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${data}=    Create Dictionary    days=90
    ${response}=    POST On Session    certificateapi    /certificates/${TEST_CERT_ID}/renew/    json=${data}    headers=${headers}
    Verify API Response Status    ${response}    200

Unauthorized Access
    [Documentation]    Testa acesso não autorizado à API
    [Tags]    regression    api    security    negative
    ${response}=    GET On Session    certificateapi    /certificates/    expected_status=401

Invalid Authorization Token
    [Documentation]    Testa token de autorização inválido
    [Tags]    regression    api    security    negative
    ${headers}=    Create Dictionary    Authorization=Bearer invalid_token
    ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}    expected_status=401

Rate Limiting
    [Documentation]    Testa limitação de taxa de requisições
    [Tags]    regression    api    security    slow
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    FOR    ${i}    IN RANGE    100
        ${response}=    GET On Session    certificateapi    /certificates/    headers=${headers}
        Exit For Loop If    ${response.status_code} == 429
    END
    Log    Rate limiting response: ${response.status_code}

*** Keywords ***
Setup API Testing
    [Documentation]    Configuração inicial para testes de API
    ${timestamp}=    Get Current Timestamp
    Set Suite Variable    ${RANDOM_SUFFIX}    ${timestamp}
    ${auth_token}=    Get API Auth Token
    Set Suite Variable    ${AUTH_TOKEN}    ${auth_token}

Teardown API Testing
    [Documentation]    Limpeza final dos testes de API
    # Cleanup pode ser adicionado aqui
    Log    API testing completed

Create Test Certificate Via API
    [Documentation]    Cria um certificado de teste via API
    ${cert_name}=    Set Variable    Test_Cert_${RANDOM_SUFFIX}
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}    Content-Type=application/json
    ${data}=    Create Dictionary    
    ...    name=${cert_name}
    ...    domain=test-setup.example.com
    ...    type=SSL
    ...    expiry_days=90
    
    ${response}=    POST On Session    certificateapi    /certificates/    json=${data}    headers=${headers}
    Verify API Response Status    ${response}    201
    ${json_data}=    Set Variable    ${response.json()}
    Set Test Variable    ${TEST_CERT_ID}    ${json_data}[id]

Get API Auth Token
    [Documentation]    Obtém token de autenticação para API
    # Implementar conforme método de autenticação da aplicação
    # Pode ser OAuth2, JWT, ou outro método
    ${token}=    Set Variable    mock_token_for_testing
    [Return]    ${token} 