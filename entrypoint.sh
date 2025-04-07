alembic upgrade head
uvicorn --host 0.0.0.0 --port 8000 fast_zero.app:app
