DOCKER_COMPOSE ?= docker compose

.PHONY: help dev dev-build dev-tools dev-down logs stage stage-down prod prod-down \
	test test-docker frontend-install frontend-lint frontend-build shell migrate \
	makemigrations superuser collectstatic install install-prod

help:
	@echo "XigmaHardware commands"
	@echo "  make dev-build       Build and start development services"
	@echo "  make dev             Start development services"
	@echo "  make dev-tools       Start optional tools such as Flower"
	@echo "  make dev-down        Stop development services"
	@echo "  make test            Run backend tests locally"
	@echo "  make test-docker     Run backend tests in Docker"
	@echo "  make frontend-build  Install, lint and build the frontend"
	@echo "  make stage           Build and start staging"
	@echo "  make prod            Build and start production"

dev:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d

dev-build:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d --build

dev-tools:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml --profile tools up -d

dev-down:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml down

logs:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f backend celery_worker celery_beat

stage:
	$(DOCKER_COMPOSE) -f docker-compose.stage.yml up -d --build

stage-down:
	$(DOCKER_COMPOSE) -f docker-compose.stage.yml down

prod:
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d --build

prod-down:
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml down

test:
	cd emarket-backend && python -m pytest -q

test-docker:
	$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm backend_test

frontend-install:
	cd xigma-frontend && npm ci

frontend-lint:
	cd xigma-frontend && npm run lint

frontend-build: frontend-install frontend-lint
	cd xigma-frontend && npm run build

shell:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec backend python manage.py shell_plus

migrate:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec backend python manage.py migrate

makemigrations:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec backend python manage.py makemigrations

superuser:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec backend python manage.py createsuperuser

collectstatic:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput

install:
	cd emarket-backend && python -m pip install -r requirements/dev.txt

install-prod:
	cd emarket-backend && python -m pip install -r requirements/prod.txt
