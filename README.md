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

### `.env.example` и `.env`

- `.env.example` — шаблон переменных окружения (хранится в репозитории).
- `.env` — ваш рабочий файл с настройками для текущего окружения (обычно не коммитится).

Пример заполнения `infra/.env` для вашего домена и IP:

```env
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,foddygramm.duckdns.org,160.5.218.182
BACKEND_IMAGE=docker.io/your_dockerhub_username/foodgram-backend:latest

DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
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

## CI/CD: Docker Hub + auto deploy

Workflow находится в `.github/workflows/ci_cd.yml` и делает следующее:

- на PR и push в `main` запускает линтер и тесты;
- на push в `main` собирает backend image и публикует в Docker Hub;
- по SSH подключается к ВМ, подтягивает `main`, делает `docker compose pull backend` и перезапускает сервисы.

Нужные GitHub Secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `SSH_HOST`
- `SSH_USER`
- `SSH_KEY`
- `SSH_PORT` (опционально, по умолчанию 22)
- `PROJECT_DIR` (путь до репозитория на ВМ)

Опционально, для автоматического создания/обновления админа при деплое:

- `ADMIN_USERNAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

Если эти 3 секрета заданы, workflow после запуска контейнеров выполнит
идемпотентный bootstrap администратора (создаст пользователя, если его нет,
или обновит email/права/пароль, если он уже существует).