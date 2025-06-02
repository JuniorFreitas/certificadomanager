# Guia de Uso - Testes Automatizados

## Instalação e Configuração

### 1. Instalar Dependências

```bash
cd robot_tests
pip install -r requirements.txt
```

### 2. Configurar Ambiente

Edite o arquivo `config/test_config.yaml` com as configurações do seu ambiente:

```yaml
test_config:
  base_url: "http://localhost:8000"
  browser: "chrome"
  headless: false
```

## Execução dos Testes

### Usando Script Bash (Linux/Mac)

```bash
# Testes básicos
./run_tests.sh smoke
./run_tests.sh regression
./run_tests.sh api
./run_tests.sh web
./run_tests.sh integration

# Com diferentes browsers
./run_tests.sh smoke firefox
./run_tests.sh smoke chrome true  # headless

# Todos os testes
./run_tests.sh all

# Execução paralela
./run_tests.sh parallel
```

### Usando Script Python (Multiplataforma)

```bash
# Testes básicos
python run_tests.py --type smoke
python run_tests.py --type regression --parallel
python run_tests.py --type api

# Com opções específicas
python run_tests.py --type web --browser firefox --headless
python run_tests.py --type security
python run_tests.py --include smoke regression --exclude slow
```

### Usando Robot Framework Diretamente

```bash
# Testes específicos
robot -d results tests/web/login_tests.robot
robot -d results -i smoke tests/
robot -d results -i regression -e slow tests/

# Com variáveis
robot -d results -v BROWSER:firefox -v HEADLESS:True tests/web/

# Execução paralela
pabot -d results tests/
```

## Tipos de Testes

### 🔥 Smoke Tests
Testes críticos e rápidos que verificam funcionalidades básicas:
```bash
./run_tests.sh smoke
python run_tests.py --type smoke
```

### 🔄 Regression Tests
Testes completos de regressão:
```bash
./run_tests.sh regression
python run_tests.py --type regression --parallel
```

### 🌐 Web Tests
Testes de interface web:
```bash
./run_tests.sh web
python run_tests.py --type web --browser chrome
```

### 🔌 API Tests
Testes de API REST:
```bash
./run_tests.sh api
python run_tests.py --type api
```

### 🔗 Integration Tests
Testes de integração end-to-end:
```bash
./run_tests.sh integration
python run_tests.py --type integration
```

### 🔒 Security Tests
Testes de segurança:
```bash
python run_tests.py --type security
```

## Tags Disponíveis

- `smoke` - Testes críticos e rápidos
- `regression` - Testes de regressão
- `api` - Testes de API
- `web` - Testes de interface
- `integration` - Testes de integração
- `negative` - Testes de casos negativos
- `security` - Testes de segurança
- `slow` - Testes que demoram mais
- `certificates` - Testes de certificados
- `users` - Testes de usuários
- `monitoring` - Testes de monitoramento

## Browsers Suportados

- `chrome` (padrão)
- `firefox`
- `safari` (apenas macOS)
- `headlesschrome`

## Relatórios

Os relatórios são gerados na pasta `results/` com timestamp:

```
results/
├── smoke_20241201_143022/
│   ├── report.html      # Relatório visual
│   ├── log.html         # Log detalhado
│   └── output.xml       # Dados para CI/CD
```

### Visualizar Relatórios

1. Abra `report.html` no browser para ver resultados visuais
2. Abra `log.html` para ver logs detalhados
3. Use `output.xml` para integração com CI/CD

## Configurações Avançadas

### Variáveis de Ambiente

```bash
export ROBOT_BROWSER=firefox
export ROBOT_HEADLESS=true
export ROBOT_TIMEOUT=60
```

### Configuração de CI/CD

Use o arquivo `config/github_actions.yml` como base para GitHub Actions.

### Execução em Docker

```bash
# Build da imagem
docker build -t robot-tests .

# Execução
docker run --rm -v $(pwd)/results:/app/results robot-tests
```

## Debugging

### Screenshots

Screenshots são capturados automaticamente em falhas e salvos em `results/screenshots/`.

### Logs Detalhados

```bash
robot -d results -L DEBUG tests/
```

### Modo Interativo

```bash
# Executar sem headless para ver o browser
python run_tests.py --type smoke --browser chrome
```

## Melhores Práticas

### 1. Organização dos Testes

- Use tags apropriadas
- Mantenha testes independentes
- Implemente cleanup adequado

### 2. Dados de Teste

- Use dados únicos (timestamps)
- Limpe dados após testes
- Use factories para criação de dados

### 3. Seletores

- Prefira IDs e classes CSS
- Evite XPath complexos
- Use Page Object Model

### 4. Timeouts

- Configure timeouts apropriados
- Use waits explícitos
- Considere performance da aplicação

## Troubleshooting

### Problemas Comuns

1. **Servidor Django não inicia**
   ```bash
   cd .. && python manage.py runserver
   ```

2. **Browser não encontrado**
   ```bash
   # Instalar ChromeDriver
   pip install webdriver-manager
   ```

3. **Dependências faltando**
   ```bash
   pip install -r requirements.txt
   ```

4. **Permissões de execução**
   ```bash
   chmod +x run_tests.sh run_tests.py
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
robot -d results -L TRACE tests/

# Verificar logs do Django
tail -f ../logs/django.log
```

## Integração com IDEs

### VS Code

Instale a extensão "Robot Framework Language Server" para:
- Syntax highlighting
- Auto-completion
- Debugging

### PyCharm

Configure o interpretador Python e adicione as bibliotecas Robot Framework.

## Contribuindo

1. Adicione novos testes seguindo a estrutura existente
2. Use tags apropriadas
3. Documente keywords customizadas
4. Mantenha compatibilidade com CI/CD

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `results/`
2. Consulte a documentação do Robot Framework
3. Abra uma issue no repositório 