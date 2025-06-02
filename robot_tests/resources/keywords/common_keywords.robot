*** Settings ***
Library    SeleniumLibrary
Library    RequestsLibrary
Library    Collections
Library    String
Library    DateTime
Library    OperatingSystem
Variables  ../variables/common_variables.robot

*** Keywords ***
Setup Browser
    [Documentation]    Configura o browser para os testes
    [Arguments]    ${browser}=${BROWSER}    ${headless}=${HEADLESS}
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Run Keyword If    '${headless}' == 'True'    Call Method    ${options}    add_argument    --headless
    Call Method    ${options}    add_argument    --no-sandbox
    Call Method    ${options}    add_argument    --disable-dev-shm-usage
    Open Browser    ${BASE_URL}    ${browser}    options=${options}
    Maximize Browser Window
    Set Selenium Timeout    ${TIMEOUT}
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}

Teardown Browser
    [Documentation]    Fecha o browser após os testes
    Close All Browsers

Navigate To Page
    [Documentation]    Navega para uma página específica
    [Arguments]    ${page_path}
    ${url}=    Set Variable    ${BASE_URL}${page_path}
    Go To    ${url}
    Wait Until Page Contains Element    tag=body

Login As User
    [Documentation]    Realiza login com um usuário específico
    [Arguments]    ${username}    ${password}
    Navigate To Page    /login/
    Wait Until Page Contains Element    ${LOGIN_USERNAME_FIELD}
    Input Text    ${LOGIN_USERNAME_FIELD}    ${username}
    Input Password    ${LOGIN_PASSWORD_FIELD}    ${password}
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Wait Until Page Contains    ${LOGIN_SUCCESS_MSG}    timeout=${TIMEOUT}

Login As Admin
    [Documentation]    Realiza login como administrador
    Login As User    ${ADMIN_USERNAME}    ${ADMIN_PASSWORD}

Login As Regular User
    [Documentation]    Realiza login como usuário regular
    Login As User    ${USER_USERNAME}    ${USER_PASSWORD}

Login As Manager
    [Documentation]    Realiza login como gerente
    Login As User    ${MANAGER_USERNAME}    ${MANAGER_PASSWORD}

Logout User
    [Documentation]    Realiza logout do usuário atual
    Click Link    ${LOGOUT_LINK}
    Wait Until Page Contains    ${LOGOUT_SUCCESS_MSG}    timeout=${TIMEOUT}

Verify Page Title
    [Documentation]    Verifica o título da página
    [Arguments]    ${expected_title}
    Title Should Be    ${expected_title}

Verify Page Contains Text
    [Documentation]    Verifica se a página contém o texto especificado
    [Arguments]    ${text}
    Page Should Contain    ${text}

Verify Element Is Visible
    [Documentation]    Verifica se um elemento está visível
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    timeout=${TIMEOUT}

Verify Element Is Not Visible
    [Documentation]    Verifica se um elemento não está visível
    [Arguments]    ${locator}
    Element Should Not Be Visible    ${locator}

Take Screenshot On Failure
    [Documentation]    Captura screenshot em caso de falha
    Run Keyword If Test Failed    Capture Page Screenshot

Create Test User
    [Documentation]    Cria um usuário de teste via API
    [Arguments]    ${username}    ${email}    ${password}    ${first_name}=Test    ${last_name}=User
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${data}=    Create Dictionary    
    ...    username=${username}
    ...    email=${email}
    ...    password=${password}
    ...    first_name=${first_name}
    ...    last_name=${last_name}
    ${response}=    POST    ${API_BASE_URL}/users/    json=${data}    headers=${headers}
    [Return]    ${response}

Delete Test User
    [Documentation]    Remove um usuário de teste via API
    [Arguments]    ${user_id}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    DELETE    ${API_BASE_URL}/users/${user_id}/    headers=${headers}
    [Return]    ${response}

Wait For Ajax
    [Documentation]    Aguarda requisições AJAX terminarem
    [Arguments]    ${timeout}=${TIMEOUT}
    Wait For Condition    return jQuery.active == 0    timeout=${timeout}

Generate Random String
    [Documentation]    Gera uma string aleatória
    [Arguments]    ${length}=10
    ${random_string}=    Generate Random String    ${length}
    [Return]    ${random_string}

Get Current Timestamp
    [Documentation]    Retorna timestamp atual
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    [Return]    ${timestamp}

Verify API Response Status
    [Documentation]    Verifica status code da resposta da API
    [Arguments]    ${response}    ${expected_status}
    Should Be Equal As Strings    ${response.status_code}    ${expected_status}

Verify API Response Contains
    [Documentation]    Verifica se resposta da API contém dados específicos
    [Arguments]    ${response}    ${key}    ${expected_value}
    ${json_data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json_data}    ${key}
    Should Be Equal As Strings    ${json_data}[${key}]    ${expected_value} 