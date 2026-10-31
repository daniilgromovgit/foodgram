# Foodgram

Учебный проект сервиса рецептов.

## Статус

Реализованы базовые API и пользовательские сценарии для рецептов,
избранного, корзины, подписок, аватара и выгрузки списка покупок.

## Структура

- `frontend/` — frontend-приложение
- `backend/` — Django backend
- `infra/` — Docker и nginx
- `docs/` — документация и схема базы данных

## Backend (локально)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py load_ingredients
python manage.py runserver
```

## Запуск в Docker

```bash
cd infra
cp .env.example .env
docker compose up -d --build
```

## Доступные адреса

- `http://localhost/` — frontend
- `http://localhost/api/` — API
- `http://localhost/admin/` — админ-зона
- `http://localhost/api/docs/` — документация

## Локальный запуск frontend

```bash
cd infra
docker compose up
```
## После запуска
- http://localhost — приложение
- http://localhost/api/docs/ — документация API