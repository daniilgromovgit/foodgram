FROM python:3.14-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
