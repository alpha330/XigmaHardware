# ============================================================
# Marketplace - Main Makefile
# ============================================================

.PHONY: help dev stage prod test build logs shell migrate clean

# Default target
help:
	@echo "Marketplace Management Commands"
	@echo "================================"
	@echo "make dev          - Start development environment"
	@echo "make dev-build    - Build and start development"
	@echo "make dev-down     - Stop development"
	@echo "make stage        - Start staging environment"
	@echo "make prod         - Start production environment"
	@echo "make test         - Run tests"
	@echo "make logs         - Show backend logs"
	@echo "make shell        - Django shell"
	@echo "make migrate      - Run migrations"
	@echo "make superuser    - Create superuser"
	@echo "make clean        - Clean everything"
	@echo "make install      - Install requirements"
	@echo ""

# ==================== Development ====================
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started"
	@echo "📚 API: http://localhost:8000/swagger/"
	@echo "📧 MailHog: http://localhost:8025/"
	@echo "🌸 Flower: http://localhost:5555/"

dev-build:
	docker-compose -f docker-compose.dev.yml up -d --build
	@echo "✅ Development environment built and started"

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-restart:
	docker-compose -f docker-compose.dev.yml restart

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f backend

dev-all-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# ==================== Staging ====================
stage:
	docker-compose -f docker-compose.stage.yml up -d --build

stage-down:
	docker-compose -f docker-compose.stage.yml down

# ==================== Production ====================
prod:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down

# ==================== Testing ====================
test:
	cd emarket-backend && pytest

test-cov:
	cd emarket-backend && pytest --cov=apps --cov-report=html

test-docker:
	docker-compose -f docker-compose.dev.yml exec backend pytest

# ==================== Backend Commands ====================
shell:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py shell_plus

migrate:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

makemigrations:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py makemigrations

superuser:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

collectstatic:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput

# ==================== Data ====================
create-dev-data:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py create_dev_data

create-dev-data-clean:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py create_dev_data --clean

# ==================== Quality ====================
lint:
	cd emarket-backend && black .
	cd emarket-backend && isort .
	cd emarket-backend && flake8 .

format:
	cd emarket-backend && black .
	cd emarket-backend && isort .

# ==================== Install ====================
install:
	cd emarket-backend && pip install -r requirements/dev.txt

install-prod:
	cd emarket-backend && pip install -r requirements/prod.txt

# ==================== Clean ====================
clean:
	docker-compose -f docker-compose.dev.yml down -v
	find emarket-backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find emarket-backend -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned everything"

clean-docker:
	docker system prune -f
	docker volume prune -f

# ==================== Git ====================
git-pull:
	git pull origin main

git-push:
	git add .
	git commit -m "$(msg)" || true
	git push origin main

# ==================== Urls ====================
urls:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py show_urls