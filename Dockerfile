FROM python:latest
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
EXPOSE 8080
CMD uvicorn --host 0.0.0.0 fast_zero.app:app
