# Conteúdo para: Makefile

# Define o nome do projeto para os containers Docker
COMPOSE_PROJECT_NAME=juribot

# Alvo padrão: exibe uma ajuda amigável
.PHONY: help
help:
	@echo "----------------------------------------------------"
	@echo " Comandos disponíveis para o projeto Juribot:"
	@echo "----------------------------------------------------"
	@echo " make up           - Sobe todos os serviços com Docker Compose"
	@echo " make down         - Para e remove todos os serviços"
	@echo " make build        - Força a reconstrução das imagens Docker"
	@echo " make logs         - Mostra os logs de todos os serviços"
	@echo " make logs-api     - Mostra os logs apenas do serviço da API (backend)"
	@echo " make logs-web     - Mostra os logs apenas do serviço da Web (frontend)"
	@echo " make shell-api    - Acessa o terminal (shell) dentro do container da API"
	@echo " make ingest       - Executa o script de ingestão de documentos (dentro do container)"
	@echo " make eval         - Executa o script de avaliação do sistema RAG (dentro do container)"
	@echo "----------------------------------------------------"

# Sobe os containers em modo 'detached' (background)
.PHONY: up
up:
	docker-compose -p $(COMPOSE_PROJECT_NAME) up -d --build

# Para e remove os containers, redes e volumes
.PHONY: down
down:
	docker-compose -p $(COMPOSE_PROJECT_NAME) down

# Força a reconstrução das imagens sem usar o cache
.PHONY: build
build:
	docker-compose -p $(COMPOSE_PROJECT_NAME) build --no-cache

# Mostra os logs de todos os containers
.PHONY: logs
logs:
	docker-compose -p $(COMPOSE_PROJECT_NAME) logs -f

# Mostra os logs do container da API
.PHONY: logs-api
logs-api:
	docker-compose -p $(COMPOSE_PROJECT_NAME) logs -f api

# Mostra os logs do container do frontend
.PHONY: logs-web
logs-web:
	docker-compose -p $(COMPOSE_PROJECT_NAME) logs -f frontend

# Acessa o terminal interativo do container da API
.PHONY: shell-api
shell-api:
	docker-compose -p $(COMPOSE_PROJECT_NAME) exec api /bin/bash

# Executa o script de ingestão de dados
.PHONY: ingest
ingest:
	@echo "🚀 Iniciando ingestão de documentos..."
	docker-compose -p $(COMPOSE_PROJECT_NAME) exec api python -m ingest.prepare_index

# Executa o script de avaliação
.PHONY: eval
eval:
	@echo "📊 Executando avaliação do sistema..."
	docker-compose -p $(COMPOSE_PROJECT_NAME) exec api python -m eval.eval_runner