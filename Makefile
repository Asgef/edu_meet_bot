MANAGE := poetry run

.PHONY: migrate

install:
	poetry install

start:
	${MANAGE} start

lint:
	${MANAGE} flake8 .

migrate:
	${MANAGE} alembic revision --autogenerate

upgrade_head:
	${MANAGE} alembic upgrade head