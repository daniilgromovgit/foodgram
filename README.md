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
git clone https://github.com/your_username/foodgram.git
cd foodgram
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py load_ingredients
python manage.py load_tags
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

- [Frontend](http://localhost/) 
- [API](http://localhost/api/) 
- [Админ-зона](http://localhost/admin/) 
- [Документация API](http://localhost/api/docs/) 

## Адрес сайта

- [Production](http://foddygramm.duckdns.org/)

## Локальный запуск frontend

```bash
cd infra
docker compose up
```
## После запуска
- [Приложение](http://localhost)
- [Документация API](http://localhost/api/docs/)

## CI/CD: auto deploy

Workflow находится в `.github/workflows/ci_cd.yml` и делает следующее:

- на PR и push в `main` запускает линтер и тесты;
- на push в `main` собирает backend image и передаёт его на ВМ по SSH;
- запускает миграции и подготовку ревью-данных.

Если Docker Engine или Compose plugin отсутствуют, workflow установит их на Ubuntu-ВМ
из системных пакетов и запустит Docker. Для этого `SSH_USER` должен иметь
passwordless `sudo`. На других ОС Docker нужно установить вручную.
Docker включается при загрузке системы, а PostgreSQL, backend и nginx настроены
на автоматический запуск после перезагрузки ВМ.

Нужные GitHub Secrets:

- `SSH_HOST`
- `SSH_USER`
- `SSH_KEY`
- `SSH_PORT` (опционально, по умолчанию 22)
- `PROJECT_DIR` (путь до директории деплоя на ВМ)

После деплоя workflow также автоматически выполняет:

- `python manage.py migrate --noinput`
- `python manage.py prepare_review_data`

Для подготовки ревью-данных на сервере:

```bash
docker compose exec backend python manage.py prepare_review_data
```

Команда обеспечивает:

- доступ в админку: `review` / `review@admin.ru` / `revw1admn`;
- минимум 7 рецептов, из них минимум 4 у одного пользователя, отличного от `review`.

## Автор

- ФИО: Громов Даниил Николаевич
- Контакт: [GitHub](https://github.com/daniilgromovgit)