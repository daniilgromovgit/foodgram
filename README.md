# Foodgram

Учебный проект сервиса рецептов.

## Статус

Проект находится на этапе проектирования моделей и базовой настройки backend.

## Структура

- `frontend/` — frontend-приложение
- `backend/` — Django backend
- `infra/` — Docker и nginx
- `docs/` — документация и схема базы данных

## Локальный запуск frontend

```bash
cd infra
docker compose up
```
## После запуска
- http://localhost — приложение
- http://localhost/api/docs/ — документация API