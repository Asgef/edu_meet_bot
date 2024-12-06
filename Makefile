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