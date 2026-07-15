# AI Agent Backend


## Переменные окружения

Скопируйте `.env.example` в корне репозитория в файл `.env`:

```bash
cp .env.example .env
```


## Запуск через Docker Compose

В корне репозитория выполните:

```bash
docker compose up --build
```

После запуска сервис будет доступен на:

- http://localhost:8000
- OpenAPI: http://localhost:8000/docs

## Тесты

Локально из папки `ai-agent`:

```bash
cd /Users/sunnet/Desktop/ai-agent-sber/ai-agent
../myenv/bin/python -m pytest -vv
```

В контейнере:

```bash
docker compose run --rm web python -m pytest -vv
```


Описание переменных:

- `SECRET_KEY` — секретный ключ для JWT и подписи.
- `SUPER_USER_SECRET_KEY` — ключ для создания суперпользователя.
- `DATABASE_URL` — строка подключения SQLAlchemy к PostgreSQL.

## Структура

- `Dockerfile` — образ для сервиса.
- `docker-compose.yml` — запуск сервиса и PostgreSQL.
- `.env.example` — пример переменных окружения.
- `.env` — рабочая конфигурация для запуска.
- `ai-agent` — исходный код FastAPI.
