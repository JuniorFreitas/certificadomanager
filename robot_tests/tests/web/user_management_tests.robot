*** Settings ***
Documentation    Testes de gerenciamento de usuários
Library          SeleniumLibrary
Library          String
Resource         ../../resources/keywords/common_keywords.robot
Variables        ../../resources/variables/common_variables.robot
Suite Setup      Setup Browser
Suite Teardown   Teardown Browser
Test Setup       Login As Admin
Test Teardown    Test Teardown

*** Variables ***
${RANDOM_SUFFIX}    ${EMPTY}

*** Test Cases ***
Create New User
    [Documentation]    Testa criação de um novo usuário
    [Tags]    smoke    users    create
    ${username}=    Set Variable    testuser_${RANDOM_SUFFIX}
    ${email}=    Set Variable    testuser_${RANDOM_SUFFIX}@test.com
    
    Navigate To Page    /users/
    Click Link    xpath=//a[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]
    Wait Until Page Contains Element    id=id_username
    Input Text    id=id_username    ${username}
    Input Text    id=id_email    ${email}
    Input Text    id=id_first_name    Test
    Input Text    id=id_last_name    User
    Input Password    id=id_password1    testpass123
    Input Password    id=id_password2    testpass123
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Wait Until Page Contains    User created successfully

Edit User Details
    [Documentation]    Testa edição de detalhes de usuário
    [Tags]    smoke    users    edit
    ${username}=    Set Variable    edituser_${RANDOM_SUFFIX}
    
    # Primeiro criar o usuário
    Create Test User Via Web    ${username}    edituser@test.com
    
    # Editar o usuário
    Navigate To Page    /users/
    Click Link    xpath=//tr[contains(., '${username}')]//a[contains(@href, 'edit')]
    Wait Until Page Contains Element    id=id_first_name
    Clear Element Text    id=id_first_name
    Input Text    id=id_first_name    Updated
    Clear Element Text    id=id_last_name
    Input Text    id=id_last_name    Name
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Wait Until Page Contains    User updated successfully

Delete User
    [Documentation]    Testa remoção de usuário
    [Tags]    smoke    users    delete
    ${username}=    Set Variable    deleteuser_${RANDOM_SUFFIX}
    
    # Criar usuário para deletar
    Create Test User Via Web    ${username}    deleteuser@test.com
    
    # Deletar usuário
    Navigate To Page    /users/
    Click Link    xpath=//tr[contains(., '${username}')]//a[contains(@href, 'delete')]
    Wait Until Page Contains    Are you sure
    Click Button    xpath=//button[contains(text(), 'Delete') or contains(text(), 'Confirm')]
    Wait Until Page Contains    User deleted successfully

Search Users
    [Documentation]    Testa busca de usuários
    [Tags]    regression    users    search
    ${username}=    Set Variable    searchuser_${RANDOM_SUFFIX}
    
    # Criar usuário para buscar
    Create Test User Via Web    ${username}    searchuser@test.com
    
    # Buscar usuário
    Navigate To Page    /users/
    Wait Until Page Contains Element    id=search_field
    Input Text    id=search_field    ${username}
    Click Button    id=search_button
    Page Should Contain    ${username}

User Permissions Management
    [Documentation]    Testa gerenciamento de permissões de usuário
    [Tags]    regression    users    permissions
    ${username}=    Set Variable    permuser_${RANDOM_SUFFIX}
    
    # Criar usuário
    Create Test User Via Web    ${username}    permuser@test.com
    
    # Acessar página de permissões
    Navigate To Page    /users/
    Click Link    xpath=//tr[contains(., '${username}')]//a[contains(text(), 'Permissions')]
    Wait Until Page Contains    User Permissions
    
    # Adicionar permissão
    Select Checkbox    xpath=//input[@type='checkbox' and contains(@name, 'permissions')]
    Click Button    xpath=//button[contains(text(), 'Save')]
    Wait Until Page Contains    Permissions updated

User Profile View
    [Documentation]    Testa visualização de perfil de usuário
    [Tags]    smoke    users    view
    ${username}=    Set Variable    viewuser_${RANDOM_SUFFIX}
    
    # Criar usuário
    Create Test User Via Web    ${username}    viewuser@test.com
    
    # Visualizar perfil
    Navigate To Page    /users/
    Click Link    xpath=//a[contains(text(), '${username}')]
    Wait Until Page Contains    User Profile
    Page Should Contain    ${username}
    Page Should Contain    viewuser@test.com

Change User Password
    [Documentation]    Testa alteração de senha de usuário
    [Tags]    regression    users    password
    ${username}=    Set Variable    passuser_${RANDOM_SUFFIX}
    
    # Criar usuário
    Create Test User Via Web    ${username}    passuser@test.com
    
    # Alterar senha
    Navigate To Page    /users/
    Click Link    xpath=//tr[contains(., '${username}')]//a[contains(text(), 'Password')]
    Wait Until Page Contains Element    id=id_new_password1
    Input Password    id=id_new_password1    newpass123
    Input Password    id=id_new_password2    newpass123
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Password changed successfully

User Status Toggle
    [Documentation]    Testa ativação/desativação de usuário
    [Tags]    regression    users    status
    ${username}=    Set Variable    statususer_${RANDOM_SUFFIX}
    
    # Criar usuário
    Create Test User Via Web    ${username}    statususer@test.com
    
    # Desativar usuário
    Navigate To Page    /users/
    Click Link    xpath=//tr[contains(., '${username}')]//a[contains(text(), 'Deactivate')]
    Wait Until Page Contains    User deactivated
    
    # Reativar usuário
    Click Link    xpath=//tr[contains(., '${username}')]//a[contains(text(), 'Activate')]
    Wait Until Page Contains    User activated

Bulk User Operations
    [Documentation]    Testa operações em lote com usuários
    [Tags]    regression    users    bulk
    @{usernames}=    Create List
    
    # Criar múltiplos usuários
    FOR    ${i}    IN RANGE    3
        ${username}=    Set Variable    bulkuser${i}_${RANDOM_SUFFIX}
        Create Test User Via Web    ${username}    bulkuser${i}@test.com
        Append To List    ${usernames}    ${username}
    END
    
    # Selecionar usuários para operação em lote
    Navigate To Page    /users/
    FOR    ${username}    IN    @{usernames}
        Click Element    xpath=//tr[contains(., '${username}')]//input[@type='checkbox']
    END
    
    # Executar operação em lote
    Select From List By Label    id=bulk_action    Deactivate Selected
    Click Button    id=bulk_action_button
    Wait Until Page Contains    Users updated successfully

*** Keywords ***
Test Teardown
    [Documentation]    Limpeza após cada teste
    Take Screenshot On Failure
    Logout User

Create Test User Via Web
    [Documentation]    Cria um usuário de teste via interface web
    [Arguments]    ${username}    ${email}
    Navigate To Page    /users/
    Click Link    xpath=//a[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]
    Wait Until Page Contains Element    id=id_username
    Input Text    id=id_username    ${username}
    Input Text    id=id_email    ${email}
    Input Text    id=id_first_name    Test
    Input Text    id=id_last_name    User
    Input Password    id=id_password1    testpass123
    Input Password    id=id_password2    testpass123
    Click Button    xpath=//button[@type='submit' or contains(text(), 'Save')]
    Wait Until Page Contains    User created successfully 