#!/bin/bash
alembic upgrade head
uvicorn --host 0.0.0.0 --port 8080 fast_zero.app:app
