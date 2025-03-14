MANAGE := poetry run

.PHONY: migrate

install:
	poetry install

start:
	${MANAGE} start

start_production:
	nohup make start &

stop:
	pkill -f edu_meet_bot.scripts.run_bot

lint:
	${MANAGE} flake8 .

migrate:
	${MANAGE} alembic revision --autogenerate

upgrade_head:
	${MANAGE} alembic upgrade head

dev:
	docker-compose -f docker-compose.dev.yml up --build

stop-dev:
	docker-compose -f docker-compose.dev.yml down

logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f