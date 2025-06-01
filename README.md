# FCM - Finnet Certificate Manager

Sistema de gerenciamento de certificados digitais para empresas e seus clientes, desenvolvido em Django.

## 📊 Status do Projeto

- **Versão**: 1.4.0
- **Cobertura de Testes**: 87%
- **Total de Testes**: 67
- **Módulos Implementados**: 4/5 (80%)

## 🚀 Funcionalidades Implementadas

### ✅ 1. Gerenciamento de Usuários
- CRUD completo de usuários
- Autenticação por email
- Sistema de status (Ativo/Inativo)
- Interface responsiva com Bootstrap 5

### ✅ 2. Gerenciamento de Certificados
- CRUD completo de certificados
- Upload e validação de arquivos
- Busca avançada e filtros
- Alertas de expiração
- Visualização detalhada

### ✅ 3. Gerenciamento de Contas Cloud
- CRUD completo de contas AWS
- Validação de credenciais em tempo real
- Teste de conectividade
- Integração com serviços AWS (EC2, S3, RDS)
- Informações detalhadas da conta

### ✅ 4. Gerenciamento de Recursos
- CRUD completo de recursos cloud
- Suporte a 7 tipos de recursos AWS:
  - S3 (Buckets)
  - Load Balancer
  - CloudFront
  - API Gateway
  - EC2 (Instâncias)
  - RDS (Bancos de dados)
  - Lambda (Funções)
- Validação específica por tipo de recurso
- Teste de conectividade AWS
- Busca e filtros avançados
- Associação com contas cloud

### 🔄 5. Gerenciamento de Permissões (Em Desenvolvimento)
- Estrutura básica implementada
- Interface em desenvolvimento

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 4.2.16
- **Banco de Dados**: PostgreSQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Formulários**: Django Crispy Forms
- **Autenticação**: Django Auth + OAuth2
- **Cloud**: Integração AWS (boto3)
- **Testes**: Django TestCase + Coverage

## 📋 Pré-requisitos

- Python 3.9+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd certificadomanager
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados**
```bash
# Crie um banco PostgreSQL
createdb certificadomanager

# Configure as variáveis de ambiente no .env
cp .env.example .env
# Edite o .env com suas configurações
```

5. **Execute as migrações**
```bash
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Execute o servidor**
```bash
python manage.py runserver
```

## ⚙️ Configuração AWS

Para utilizar as funcionalidades de integração com AWS, configure as permissões necessárias:

### Permissões Mínimas Requeridas

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity",
                "ec2:DescribeInstances",
                "ec2:DescribeRegions",
                "s3:ListAllMyBuckets",
                "s3:HeadBucket",
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🧪 Executando Testes

```bash
# Executar todos os testes
python manage.py test

# Executar testes com cobertura
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera relatório HTML
```

## 📁 Estrutura do Projeto

```
certificadomanager/
├── apps/
│   ├── users/          # Gerenciamento de usuários
│   ├── certificates/   # Gerenciamento de certificados
│   ├── accounts/       # Gerenciamento de contas cloud
│   ├── resources/      # Gerenciamento de recursos cloud
│   └── permissions/    # Gerenciamento de permissões
├── fcm/               # Configurações do projeto
├── templates/         # Templates HTML
├── static/           # Arquivos estáticos
├── media/            # Arquivos de upload
└── requirements.txt  # Dependências
```

## 🎯 Próximos Passos

1. **Finalizar Módulo de Permissões**
   - Implementar CRUD completo
   - Sistema de roles e permissões granulares
   - Interface de gerenciamento

2. **Melhorias de Segurança**
   - Implementar 2FA
   - Logs de auditoria
   - Criptografia de dados sensíveis

3. **Funcionalidades Avançadas**
   - Dashboard com métricas avançadas
   - Relatórios e exportação
   - Notificações automáticas
   - API REST completa

4. **Integração Cloud**
   - Suporte a Azure e Google Cloud
   - Monitoramento de recursos
   - Automação de tarefas

## 📈 Métricas de Qualidade

- **Cobertura de Testes**: 87%
- **Testes Unitários**: 67
- **Padrões de Código**: PEP 8
- **Documentação**: Completa
- **Segurança**: Implementada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas, entre em contato através dos issues do GitHub ou email.

---

**FCM - Finnet Certificate Manager** - Gerenciamento profissional de certificados digitais e recursos cloud. 