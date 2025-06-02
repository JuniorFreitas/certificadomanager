*** Variables ***
# URLs base
${BASE_URL}                 http://localhost:8000
${API_BASE_URL}            http://localhost:8000/api/v1

# Configurações do Browser
${BROWSER}                 chrome
${HEADLESS}                False
${TIMEOUT}                 30s
${IMPLICIT_WAIT}           10s

# Credenciais de teste
${ADMIN_USERNAME}          admin
${ADMIN_PASSWORD}          admin123
${ADMIN_EMAIL}             admin@test.com

${USER_USERNAME}           user1
${USER_PASSWORD}           user123
${USER_EMAIL}              user1@test.com

${MANAGER_USERNAME}        manager1
${MANAGER_PASSWORD}        manager123
${MANAGER_EMAIL}           manager1@test.com

# Seletores comuns
${LOGIN_USERNAME_FIELD}    id=id_username
${LOGIN_PASSWORD_FIELD}    id=id_password
${LOGIN_SUBMIT_BUTTON}     css=button[type="submit"]
${LOGOUT_LINK}             xpath=//a[contains(@href, '/logout/')]

# Mensagens esperadas
${LOGIN_SUCCESS_MSG}       Dashboard
${LOGIN_ERROR_MSG}         Please enter a correct username and password
${LOGOUT_SUCCESS_MSG}      Login

# Dados de teste para certificados
${TEST_CERT_NAME}          Test Certificate
${TEST_CERT_DOMAIN}        test.example.com
${TEST_CERT_TYPE}          SSL
${EXPIRED_CERT_NAME}       Expired Certificate
${EXPIRED_CERT_DOMAIN}     expired.example.com

# Configurações de screenshot
${SCREENSHOT_DIR}          ${CURDIR}/../../results/screenshots
${CAPTURE_SCREENSHOTS}     True

# Configurações de relatório
${LOG_LEVEL}               INFO
${REPORT_TITLE}            Certificate Manager - Test Report 