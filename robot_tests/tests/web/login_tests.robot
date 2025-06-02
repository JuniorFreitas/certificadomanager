*** Settings ***
Documentation    Testes de autenticação e login do sistema
Library          SeleniumLibrary
Resource         ../../resources/keywords/common_keywords.robot
Variables        ../../resources/variables/common_variables.robot
Suite Setup      Setup Browser
Suite Teardown   Teardown Browser
Test Setup       Navigate To Page    /login/
Test Teardown    Take Screenshot On Failure

*** Test Cases ***
Valid Admin Login
    [Documentation]    Testa login válido com usuário administrador
    [Tags]    smoke    login    admin
    Input Text    ${LOGIN_USERNAME_FIELD}    ${ADMIN_USERNAME}
    Input Password    ${LOGIN_PASSWORD_FIELD}    ${ADMIN_PASSWORD}
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Wait Until Page Contains    ${LOGIN_SUCCESS_MSG}
    Verify Page Contains Text    Dashboard
    Verify Element Is Visible    ${LOGOUT_LINK}

Valid User Login
    [Documentation]    Testa login válido com usuário regular
    [Tags]    smoke    login    user
    Input Text    ${LOGIN_USERNAME_FIELD}    ${USER_USERNAME}
    Input Password    ${LOGIN_PASSWORD_FIELD}    ${USER_PASSWORD}
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Wait Until Page Contains    ${LOGIN_SUCCESS_MSG}
    Verify Page Contains Text    Dashboard

Invalid Login - Wrong Password
    [Documentation]    Testa login com senha incorreta
    [Tags]    regression    login    negative
    Input Text    ${LOGIN_USERNAME_FIELD}    ${ADMIN_USERNAME}
    Input Password    ${LOGIN_PASSWORD_FIELD}    wrong_password
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Wait Until Page Contains    ${LOGIN_ERROR_MSG}
    Page Should Contain    Please enter a correct username and password

Invalid Login - Wrong Username
    [Documentation]    Testa login com usuário inexistente
    [Tags]    regression    login    negative
    Input Text    ${LOGIN_USERNAME_FIELD}    wrong_user
    Input Password    ${LOGIN_PASSWORD_FIELD}    ${ADMIN_PASSWORD}
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Wait Until Page Contains    ${LOGIN_ERROR_MSG}

Invalid Login - Empty Fields
    [Documentation]    Testa login com campos vazios
    [Tags]    regression    login    negative
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Page Should Contain Element    ${LOGIN_USERNAME_FIELD}:invalid
    Page Should Contain Element    ${LOGIN_PASSWORD_FIELD}:invalid

Successful Logout
    [Documentation]    Testa logout após login válido
    [Tags]    smoke    logout
    Login As Admin
    Logout User
    Verify Page Contains Text    ${LOGOUT_SUCCESS_MSG}
    Element Should Not Be Visible    ${LOGOUT_LINK}

Login Redirect After Logout
    [Documentation]    Testa redirecionamento para login após logout
    [Tags]    regression    logout
    Login As Admin
    Navigate To Page    /certificates/
    Logout User
    Navigate To Page    /certificates/
    Wait Until Page Contains    ${LOGOUT_SUCCESS_MSG}
    Location Should Contain    /login/

Session Timeout
    [Documentation]    Testa comportamento de timeout de sessão
    [Tags]    regression    session    slow
    Login As Admin
    # Simula timeout de sessão
    Execute Javascript    document.cookie = "sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
    Navigate To Page    /certificates/
    Wait Until Page Contains    ${LOGOUT_SUCCESS_MSG}
    Location Should Contain    /login/

Remember Me Functionality
    [Documentation]    Testa funcionalidade "Lembrar de mim" se existir
    [Tags]    regression    login
    ${remember_me_exists}=    Run Keyword And Return Status    Page Should Contain Element    id=id_remember_me
    Run Keyword If    ${remember_me_exists}    Test Remember Me Feature

Password Reset Link
    [Documentation]    Testa link de redefinição de senha se existir
    [Tags]    regression    password_reset
    ${reset_link_exists}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//a[contains(text(), 'Forgot') or contains(text(), 'Reset')]
    Run Keyword If    ${reset_link_exists}    Test Password Reset Link

Multiple Failed Login Attempts
    [Documentation]    Testa múltiplas tentativas de login falhidas
    [Tags]    regression    security    negative
    FOR    ${i}    IN RANGE    3
        Input Text    ${LOGIN_USERNAME_FIELD}    wrong_user
        Input Password    ${LOGIN_PASSWORD_FIELD}    wrong_password
        Click Button    ${LOGIN_SUBMIT_BUTTON}
        Wait Until Page Contains    ${LOGIN_ERROR_MSG}
        Navigate To Page    /login/
    END
    # Verifica se há bloqueio após múltiplas tentativas
    ${lockout_message}=    Run Keyword And Return Status    Page Should Contain    account is locked
    Log    Account lockout after failed attempts: ${lockout_message}

*** Keywords ***
Test Remember Me Feature
    [Documentation]    Testa a funcionalidade "Lembrar de mim"
    Select Checkbox    id=id_remember_me
    Input Text    ${LOGIN_USERNAME_FIELD}    ${ADMIN_USERNAME}
    Input Password    ${LOGIN_PASSWORD_FIELD}    ${ADMIN_PASSWORD}
    Click Button    ${LOGIN_SUBMIT_BUTTON}
    Wait Until Page Contains    ${LOGIN_SUCCESS_MSG}
    # Fecha browser e reabre para testar persistência
    Close Browser
    Setup Browser
    Navigate To Page    /
    # Verifica se ainda está logado
    ${still_logged_in}=    Run Keyword And Return Status    Page Should Contain    Dashboard
    Log    Remember me working: ${still_logged_in}

Test Password Reset Link
    [Documentation]    Testa o link de redefinição de senha
    Click Link    xpath=//a[contains(text(), 'Forgot') or contains(text(), 'Reset')]
    Wait Until Page Contains Element    id=id_email
    Input Text    id=id_email    ${ADMIN_EMAIL}
    Click Button    xpath=//button[@type='submit']
    Page Should Contain    Password reset instructions 