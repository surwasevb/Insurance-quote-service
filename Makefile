.PHONY: help build up down restart logs shell migrate makemigrations superuser dbshell db format lint lint-fix typecheck test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop and remove all services
	docker compose down

shell: ## Open a shell in the web container
	docker compose exec web bash

migrate: ## Run Django migrations
	docker compose exec web python manage.py migrate

makemigrations: ## Create Django migrations (usage: make makemigrations ARGS=app_name)
	docker compose exec web python manage.py makemigrations $(ARGS)

superuser: ## Create a Django superuser
	docker compose exec web python manage.py createsuperuser

run: ## Run makemigrations, migrate, then start dev server
	docker compose up --build

setup: migrate makemigrations migrate ## Run initial setup (migrate + makemigrations + migrate)

db: ## Start only the database service
	docker compose up -d db

format: ## Format code with Black
	black .

lint: ## Lint code with Ruff
	ruff check .

lint-fix: ## Lint and auto-fix with Ruff
	ruff check --fix .

typecheck: ## Run type checking with mypy
	mypy .

test: db ## Run tests with pytest
	docker compose run --rm web python manage.py migrate
	pytest
