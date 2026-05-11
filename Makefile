COMPOSE ?= docker compose
BACKEND_SERVICE ?= backend

.PHONY: start stop logs migrate test build backend-test frontend-build

start:
	$(COMPOSE) --env-file .env.local up --build -d

stop:
	$(COMPOSE) --env-file .env.local down

logs:
	$(COMPOSE) --env-file .env.local logs -f

migrate:
	$(COMPOSE) --env-file .env.local run --rm $(BACKEND_SERVICE) alembic upgrade head

test:
	pytest backend/tests -q

build:
	$(COMPOSE) --env-file .env.local build

backend-test:
	pytest backend/tests -q

frontend-build:
	npm --prefix frontend run build
