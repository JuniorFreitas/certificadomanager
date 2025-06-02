# Docker Setup para Certificado Manager

Este projeto foi configurado para rodar em containers Docker com PostgreSQL, Django e Nginx.

## Pré-requisitos

- Docker
- Docker Compose

## Configuração Inicial

1. **Clone o repositório** (se ainda não fez):
```bash
git clone <seu-repositorio>
cd certificadomanager
```

2. **Crie o arquivo .env** baseado no env.example:
```bash
cp env.example .env
```

3. **Edite o arquivo .env** com as configurações para Docker:
```bash
# Django Settings
SECRET_KEY=django-insecure-development-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fcm_db
DB_USER=fcm_user
DB_PASSWORD=fcm_password
DB_HOST=db
DB_PORT=5432
```

## Como executar

### Desenvolvimento (com hot reload)

```bash
# Construir e iniciar os containers
docker-compose up --build

# Ou em background
docker-compose up -d --build
```

### Comandos úteis

```bash
# Ver logs
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f web

# Parar os containers
docker-compose down

# Parar e remover volumes (cuidado: apaga o banco de dados)
docker-compose down -v

# Executar comandos Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Acessar o shell do container
docker-compose exec web bash

# Acessar o PostgreSQL
docker-compose exec db psql -U fcm_user -d fcm_db
```

## Acessos

- **Aplicação Django**: http://localhost:8000
- **Nginx (proxy)**: http://localhost:80
- **PostgreSQL**: localhost:5432

## Usuário Padrão

O script de inicialização cria automaticamente um superusuário:
- **Usuário**: admin
- **Senha**: admin123
- **Email**: admin@example.com

## Estrutura dos Containers

### web (Django)
- Porta: 8000
- Volume: código fonte montado para desenvolvimento
- Dependências: PostgreSQL

### db (PostgreSQL)
- Porta: 5432
- Volume persistente para dados
- Credenciais definidas no docker-compose.yml

### nginx
- Porta: 80
- Proxy reverso para o Django
- Serve arquivos estáticos e media

## Volumes

- `postgres_data`: Dados do PostgreSQL
- `static_volume`: Arquivos estáticos do Django
- `media_volume`: Arquivos de media do Django

## Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs

# Reconstruir sem cache
docker-compose build --no-cache
```

### Problemas de permissão
```bash
# Dar permissão ao script de entrada
chmod +x docker-entrypoint.sh
```

### Reset completo
```bash
# Parar tudo e remover volumes
docker-compose down -v

# Remover imagens
docker-compose down --rmi all

# Reconstruir tudo
docker-compose up --build
```

## Produção

Para produção, considere:

1. Usar variáveis de ambiente seguras
2. Configurar HTTPS no Nginx
3. Usar um banco de dados externo
4. Configurar backup dos volumes
5. Usar imagens otimizadas
6. Configurar logs centralizados 