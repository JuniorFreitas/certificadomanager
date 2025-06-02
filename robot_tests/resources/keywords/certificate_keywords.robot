*** Settings ***
Library    SeleniumLibrary
Library    RequestsLibrary
Library    Collections
Library    String
Resource   common_keywords.robot
Variables  ../variables/common_variables.robot

*** Keywords ***
Navigate To Certificates Page
    [Documentation]    Navega para a página de certificados
    Navigate To Page    /certificates/
    Wait Until Page Contains    Certificates

Create New Certificate
    [Documentation]    Cria um novo certificado através da interface web
    [Arguments]    ${name}    ${domain}    ${cert_type}=SSL    ${expiry_days}=90
    Navigate To Certificates Page
    Click Link    xpath=//a[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]
    Wait Until Page Contains Element    id=id_name
    Input Text    id=id_name    ${name}
    Input Text    id=id_domain    ${domain}
    Select From List By Label    id=id_type    ${cert_type}
    Input Text    id=id_expiry_days    ${expiry_days}
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Wait Until Page Contains    Certificate created successfully

Create Certificate Via API
    [Documentation]    Cria um certificado via API
    [Arguments]    ${name}    ${domain}    ${cert_type}=SSL    ${expiry_days}=90
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${data}=    Create Dictionary    
    ...    name=${name}
    ...    domain=${domain}
    ...    type=${cert_type}
    ...    expiry_days=${expiry_days}
    ${response}=    POST    ${API_BASE_URL}/certificates/    json=${data}    headers=${headers}
    [Return]    ${response}

Edit Certificate
    [Documentation]    Edita um certificado existente
    [Arguments]    ${cert_name}    ${new_name}    ${new_domain}
    Navigate To Certificates Page
    Click Link    xpath=//tr[contains(., '${cert_name}')]//a[contains(@href, 'edit')]
    Wait Until Page Contains Element    id=id_name
    Clear Element Text    id=id_name
    Input Text    id=id_name    ${new_name}
    Clear Element Text    id=id_domain
    Input Text    id=id_domain    ${new_domain}
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Wait Until Page Contains    Certificate updated successfully

Delete Certificate
    [Documentation]    Remove um certificado
    [Arguments]    ${cert_name}
    Navigate To Certificates Page
    Click Link    xpath=//tr[contains(., '${cert_name}')]//a[contains(@href, 'delete')]
    Wait Until Page Contains    Are you sure
    Click Button    xpath=//button[contains(text(), 'Delete') or contains(text(), 'Confirm')]
    Wait Until Page Contains    Certificate deleted successfully

Verify Certificate Exists
    [Documentation]    Verifica se um certificado existe na lista
    [Arguments]    ${cert_name}
    Navigate To Certificates Page
    Page Should Contain    ${cert_name}

Verify Certificate Does Not Exist
    [Documentation]    Verifica se um certificado não existe na lista
    [Arguments]    ${cert_name}
    Navigate To Certificates Page
    Page Should Not Contain    ${cert_name}

Search Certificate
    [Documentation]    Busca por um certificado específico
    [Arguments]    ${search_term}
    Navigate To Certificates Page
    Wait Until Page Contains Element    id=search_field
    Input Text    id=search_field    ${search_term}
    Click Button    id=search_button
    Wait Until Page Contains Element    class=search-results

Filter Certificates By Status
    [Documentation]    Filtra certificados por status
    [Arguments]    ${status}
    Navigate To Certificates Page
    Select From List By Label    id=status_filter    ${status}
    Wait Until Page Contains Element    class=filtered-results

Verify Certificate Details
    [Documentation]    Verifica os detalhes de um certificado
    [Arguments]    ${cert_name}    ${expected_domain}    ${expected_type}
    Navigate To Certificates Page
    Click Link    xpath=//a[contains(text(), '${cert_name}')]
    Wait Until Page Contains    Certificate Details
    Page Should Contain    ${expected_domain}
    Page Should Contain    ${expected_type}

Check Certificate Expiry Warning
    [Documentation]    Verifica se há aviso de expiração para certificados próximos do vencimento
    [Arguments]    ${cert_name}
    Navigate To Certificates Page
    ${warning_present}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//tr[contains(., '${cert_name}')]//span[contains(@class, 'warning') or contains(@class, 'expiring')]
    [Return]    ${warning_present}

Bulk Delete Certificates
    [Documentation]    Remove múltiplos certificados em lote
    [Arguments]    @{cert_names}
    Navigate To Certificates Page
    FOR    ${cert_name}    IN    @{cert_names}
        Click Element    xpath=//tr[contains(., '${cert_name}')]//input[@type='checkbox']
    END
    Click Button    id=bulk_delete_button
    Wait Until Page Contains    Are you sure
    Click Button    xpath=//button[contains(text(), 'Delete Selected')]
    Wait Until Page Contains    Certificates deleted successfully

Export Certificates List
    [Documentation]    Exporta lista de certificados
    [Arguments]    ${format}=CSV
    Navigate To Certificates Page
    Click Button    id=export_button
    Select From List By Label    id=export_format    ${format}
    Click Button    xpath=//button[contains(text(), 'Export')]

Import Certificates
    [Documentation]    Importa certificados de um arquivo
    [Arguments]    ${file_path}
    Navigate To Certificates Page
    Click Link    xpath=//a[contains(text(), 'Import')]
    Choose File    id=import_file    ${file_path}
    Click Button    xpath=//button[contains(text(), 'Import')]
    Wait Until Page Contains    Import completed

Verify Certificate Monitoring Alert
    [Documentation]    Verifica se há alertas de monitoramento para um certificado
    [Arguments]    ${cert_name}
    Navigate To Page    /monitoring/
    Page Should Contain    ${cert_name}
    ${alert_present}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//tr[contains(., '${cert_name}')]//span[contains(@class, 'alert')]
    [Return]    ${alert_present}

Renew Certificate
    [Documentation]    Renova um certificado existente
    [Arguments]    ${cert_name}
    Navigate To Certificates Page
    Click Link    xpath=//tr[contains(., '${cert_name}')]//a[contains(text(), 'Renew')]
    Wait Until Page Contains    Renew Certificate
    Click Button    xpath=//button[contains(text(), 'Renew')]
    Wait Until Page Contains    Certificate renewed successfully 