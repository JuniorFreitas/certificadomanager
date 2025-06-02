# Testes Automatizados - Certificate Manager

Este projeto contém os testes automatizados para o sistema Certificate Manager usando Robot Framework.

## Estrutura dos Testes

```
robot_tests/
├── tests/
│   ├── web/               # Testes de interface web
│   ├── api/               # Testes de API
│   └── integration/       # Testes de integração
├── resources/
│   ├── keywords/          # Keywords customizadas
│   ├── variables/         # Variáveis de configuração
│   └── data/             # Dados de teste
├── libraries/            # Bibliotecas Python customizadas
├── results/              # Resultados dos testes
└── config/               # Configurações de ambiente

```

## Instalação

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente no arquivo `config/test_config.yaml`

## Execução dos Testes

### Todos os testes
```bash
robot -d results tests/
```

### Testes específicos
```bash
# Apenas testes web
robot -d results tests/web/

# Apenas testes de API
robot -d results tests/api/

# Por tags
robot -d results -i smoke tests/
robot -d results -i regression tests/
```

### Com diferentes browsers
```bash
robot -d results -v BROWSER:chrome tests/web/
robot -d results -v BROWSER:firefox tests/web/
robot -d results -v BROWSER:headlesschrome tests/web/
```

### Execução em paralelo
```bash
pabot -d results tests/
```

## Relatórios

Os relatórios são gerados na pasta `results/` e incluem:
- `report.html` - Relatório detalhado dos testes
- `log.html` - Log detalhado da execução
- `output.xml` - Dados em XML para integração com CI/CD

## Integração com CI/CD

Os testes podem ser facilmente integrados com:
- GitHub Actions
- Jenkins
- GitLab CI
- Azure DevOps

Exemplo de configuração no `.github/workflows/robot-tests.yml` está disponível na pasta config.

## Tags dos Testes

- `smoke` - Testes críticos e rápidos
- `regression` - Testes completos de regressão
- `api` - Testes de API
- `web` - Testes de interface
- `database` - Testes de banco de dados
- `integration` - Testes de integração
- `slow` - Testes que demoram mais para executar 