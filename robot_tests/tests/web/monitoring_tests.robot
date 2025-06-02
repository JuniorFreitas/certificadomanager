*** Settings ***
Documentation    Testes do sistema de monitoramento de certificados
Library          SeleniumLibrary
Library          String
Resource         ../../resources/keywords/common_keywords.robot
Resource         ../../resources/keywords/certificate_keywords.robot
Variables        ../../resources/variables/common_variables.robot
Suite Setup      Setup Browser
Suite Teardown   Teardown Browser
Test Setup       Login As Admin
Test Teardown    Test Teardown

*** Variables ***
${RANDOM_SUFFIX}    ${EMPTY}

*** Test Cases ***
View Monitoring Dashboard
    [Documentation]    Testa visualização do dashboard de monitoramento
    [Tags]    smoke    monitoring    dashboard
    Navigate To Page    /monitoring/
    Wait Until Page Contains    Certificate Monitoring
    Page Should Contain Element    class=monitoring-stats
    Page Should Contain Element    class=expiring-certificates

Check Expiring Certificates Alert
    [Documentation]    Testa alertas de certificados próximos ao vencimento
    [Tags]    smoke    monitoring    alerts
    ${cert_name}=    Set Variable    ExpiringCert_${RANDOM_SUFFIX}
    
    # Criar certificado próximo ao vencimento
    Create New Certificate    ${cert_name}    expiring.example.com    SSL    5
    
    # Verificar no monitoramento
    Navigate To Page    /monitoring/
    Page Should Contain    ${cert_name}
    Page Should Contain Element    xpath=//tr[contains(., '${cert_name}')]//span[contains(@class, 'alert-warning')]

Check Expired Certificates Alert
    [Documentation]    Testa alertas de certificados expirados
    [Tags]    regression    monitoring    alerts
    ${cert_name}=    Set Variable    ExpiredCert_${RANDOM_SUFFIX}
    
    # Criar certificado "expirado" (simulado)
    Create New Certificate    ${cert_name}    expired.example.com    SSL    -5
    
    # Verificar no monitoramento
    Navigate To Page    /monitoring/
    Page Should Contain    ${cert_name}
    Page Should Contain Element    xpath=//tr[contains(., '${cert_name}')]//span[contains(@class, 'alert-danger')]

Filter Monitoring By Status
    [Documentation]    Testa filtros no monitoramento
    [Tags]    regression    monitoring    filter
    Navigate To Page    /monitoring/
    
    # Filtrar por certificados expirados
    Select From List By Label    id=status_filter    Expired
    Click Button    id=filter_button
    Wait Until Page Contains Element    class=filtered-results
    
    # Filtrar por certificados próximos ao vencimento
    Select From List By Label    id=status_filter    Expiring Soon
    Click Button    id=filter_button
    Wait Until Page Contains Element    class=filtered-results

Monitoring Statistics View
    [Documentation]    Testa visualização de estatísticas de monitoramento
    [Tags]    smoke    monitoring    stats
    Navigate To Page    /monitoring/stats/
    Wait Until Page Contains    Monitoring Statistics
    Page Should Contain Element    id=total-certificates
    Page Should Contain Element    id=active-certificates
    Page Should Contain Element    id=expired-certificates
    Page Should Contain Element    id=expiring-soon

Email Notification Settings
    [Documentation]    Testa configurações de notificação por email
    [Tags]    regression    monitoring    notifications
    Navigate To Page    /monitoring/settings/
    Wait Until Page Contains    Notification Settings
    
    # Configurar notificações
    Select Checkbox    id=email_notifications
    Input Text    id=notification_email    admin@test.com
    Select From List By Label    id=notification_frequency    Daily
    Click Button    xpath=//button[contains(text(), 'Save')]
    Wait Until Page Contains    Settings saved successfully

Certificate Health Check
    [Documentation]    Testa verificação de saúde dos certificados
    [Tags]    regression    monitoring    health
    ${cert_name}=    Set Variable    HealthCheck_${RANDOM_SUFFIX}
    
    # Criar certificado para verificação
    Create New Certificate    ${cert_name}    health.example.com    SSL    30
    
    # Executar verificação de saúde
    Navigate To Page    /monitoring/
    Click Link    xpath=//tr[contains(., '${cert_name}')]//a[contains(text(), 'Check Health')]
    Wait Until Page Contains    Health check completed
    Page Should Contain Element    xpath=//tr[contains(., '${cert_name}')]//span[contains(@class, 'health-status')]

Monitoring Reports Generation
    [Documentation]    Testa geração de relatórios de monitoramento
    [Tags]    regression    monitoring    reports
    Navigate To Page    /monitoring/reports/
    Wait Until Page Contains    Monitoring Reports
    
    # Gerar relatório mensal
    Select From List By Label    id=report_type    Monthly Summary
    Select From List By Label    id=report_format    PDF
    Click Button    id=generate_report
    Wait Until Page Contains    Report generated successfully

Monitoring API Integration
    [Documentation]    Testa integração com API de monitoramento
    [Tags]    integration    monitoring    api
    Navigate To Page    /monitoring/api/
    Wait Until Page Contains    API Integration
    
    # Verificar endpoints disponíveis
    Page Should Contain    /api/monitoring/status
    Page Should Contain    /api/monitoring/alerts
    Page Should Contain    /api/monitoring/stats

Real-time Monitoring Updates
    [Documentation]    Testa atualizações em tempo real do monitoramento
    [Tags]    regression    monitoring    realtime
    Navigate To Page    /monitoring/
    
    # Verificar se há atualizações automáticas
    ${auto_refresh}=    Run Keyword And Return Status    Page Should Contain Element    id=auto-refresh
    Run Keyword If    ${auto_refresh}    Test Auto Refresh Feature

Monitoring Alerts Configuration
    [Documentation]    Testa configuração de alertas de monitoramento
    [Tags]    regression    monitoring    alerts
    Navigate To Page    /monitoring/alerts/
    Wait Until Page Contains    Alert Configuration
    
    # Configurar alerta para certificados próximos ao vencimento
    Input Text    id=expiry_warning_days    30
    Select Checkbox    id=enable_email_alerts
    Select Checkbox    id=enable_dashboard_alerts
    Click Button    xpath=//button[contains(text(), 'Save')]
    Wait Until Page Contains    Alert configuration saved

Monitoring History View
    [Documentation]    Testa visualização do histórico de monitoramento
    [Tags]    regression    monitoring    history
    Navigate To Page    /monitoring/history/
    Wait Until Page Contains    Monitoring History
    
    # Filtrar por período
    Input Text    id=date_from    2024-01-01
    Input Text    id=date_to    2024-12-31
    Click Button    id=filter_history
    Wait Until Page Contains Element    class=history-results

*** Keywords ***
Test Teardown
    [Documentation]    Limpeza após cada teste
    Take Screenshot On Failure
    Logout User

Test Auto Refresh Feature
    [Documentation]    Testa funcionalidade de atualização automática
    # Verificar se o refresh automático está funcionando
    ${initial_time}=    Get Text    id=last-update-time
    Sleep    5s
    ${updated_time}=    Get Text    id=last-update-time
    Should Not Be Equal    ${initial_time}    ${updated_time} 