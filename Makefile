.PHONY: help build up down logs shell migrate createsuperuser collectstatic clean reset

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Constrói as imagens Docker
	docker-compose build

up: ## Inicia os containers
	docker-compose up

up-d: ## Inicia os containers em background
	docker-compose up -d

down: ## Para os containers
	docker-compose down

logs: ## Mostra os logs de todos os containers
	docker-compose logs -f

logs-web: ## Mostra os logs do container web
	docker-compose logs -f web

logs-db: ## Mostra os logs do container db
	docker-compose logs -f db

shell: ## Acessa o shell do container web
	docker-compose exec web bash

shell-db: ## Acessa o PostgreSQL
	docker-compose exec db psql -U fcm_user -d fcm_db

migrate: ## Executa as migrações do Django
	docker-compose exec web python manage.py migrate

makemigrations: ## Cria novas migrações
	docker-compose exec web python manage.py makemigrations

createsuperuser: ## Cria um superusuário
	docker-compose exec web python manage.py createsuperuser

collectstatic: ## Coleta arquivos estáticos
	docker-compose exec web python manage.py collectstatic --noinput

test: ## Executa os testes
	docker-compose exec web python manage.py test

clean: ## Remove containers parados e imagens não utilizadas
	docker system prune -f

reset: ## Reset completo - remove tudo e reconstrói
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

dev: ## Inicia ambiente de desenvolvimento
	@echo "Iniciando ambiente de desenvolvimento..."
	docker-compose up --build

prod-build: ## Constrói para produção
	docker-compose -f docker-compose.prod.yml build

status: ## Mostra status dos containers
	docker-compose ps 