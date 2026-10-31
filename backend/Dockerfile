FROM python:3.14-slim

WORKDIR /app/backend

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY backend /app/backend
COPY data /app/data

RUN chmod +x /app/backend/entrypoint.sh

ENTRYPOINT ["/app/backend/entrypoint.sh"]
