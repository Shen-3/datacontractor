.PHONY: install dev test lint format migrate seed api dashboard demo-valid demo-invalid-schema demo-invalid-enum demo-nulls demo-duplicates demo-stale docker-up docker-down clean

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

lint:
	ruff check app tests

format:
	ruff format app tests
	black app tests

migrate:
	alembic upgrade head

seed:
	python scripts/seed_demo_data.py

api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dashboard:
	streamlit run app/dashboard/streamlit_app.py

demo-valid:
	python -m datacontractor.etl.run --dataset data/datasets/users_events_valid.csv --contract users_events

demo-invalid-schema:
	python -m datacontractor.etl.run --dataset data/datasets/users_events_missing_field.csv --contract users_events

demo-invalid-enum:
	python -m datacontractor.etl.run --dataset data/datasets/users_events_invalid_enum.csv --contract users_events

demo-nulls:
	python -m datacontractor.etl.run --dataset data/datasets/users_events_nulls.csv --contract users_events

demo-duplicates:
	python -m datacontractor.etl.run --dataset data/datasets/users_events_duplicates.csv --contract users_events

demo-stale:
	python -m datacontractor.etl.run --dataset data/datasets/users_events_stale.csv --contract users_events

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache *.egg-info dist build
