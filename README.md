# FCM - Finnet Certificate Manager

Sistema de gestão de certificados digitais para controle e atualização de certificados utilizados pela empresa e clientes.

## Funcionalidades

- **Gestão de Usuários**: Cadastro, edição e exclusão de usuários com controle de permissões
- **Gestão de Certificados**: Controle completo do ciclo de vida dos certificados
- **Gestão de Contas Cloud**: Configuração de contas AWS para integração
- **Gestão de Recursos**: Cadastro de recursos cloud (S3, Load Balancer, etc.)
- **Sistema de Permissões**: Controle granular de acesso às funcionalidades

## Tecnologias

- Python 3.11+
- Django 5.0
- PostgreSQL
- Bootstrap 5
- AWS SDK (boto3)
- OAuth2

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd certificadomanager
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Crie um superusuário:
```bash
python manage.py createsuperuser
```

7. Execute o servidor:
```bash
python manage.py runserver
```

## Configuração do Banco de Dados

Configure o PostgreSQL e atualize as variáveis no arquivo `.env`:

```
DB_NAME=fcm_db
DB_USER=fcm_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Testes

Execute os testes com cobertura:
```bash
pytest --cov=. --cov-report=html
```

## Estrutura do Projeto

```
certificadomanager/
├── fcm/                    # Projeto principal
├── apps/
│   ├── users/             # Gestão de usuários
│   ├── certificates/      # Gestão de certificados
│   ├── accounts/          # Gestão de contas cloud
│   ├── resources/         # Gestão de recursos
│   └── permissions/       # Sistema de permissões
├── static/                # Arquivos estáticos
├── templates/             # Templates HTML
└── requirements.txt       # Dependências
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 