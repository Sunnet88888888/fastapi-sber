# AI Agent Backend

Infrastructure: 
`Python3`, `FastAPI`, `SQLAlchemy`, `Alembic`, `Argon2`, `PostgreSQL`, `Docker`, `Docker-compose`

Guide to run the project: 

1) Clone the project

```bash
git clone https://github.com/Sunnet88888888/fastapi-sber.git
```
2) Change directory
```bash
cd fastapi-sber
```
3) Create .env file and copy .env.example

```bash
touch .env
cp .env.example .env
```
4) Change values of secret keys in .env file

<img width="624" height="109" alt="Снимок экрана 2026-07-15 в 08 58 56" src="https://github.com/user-attachments/assets/6a8f72ec-a77c-4dde-a012-81341b135c0d" />

SECRET_KEY is for jwt
SUPER_USER_SECRET_KEY is your superuser key to create admins
DATABASE_URL can be changed as you prefer.(Anyway it runs in docker)

5) Run docker-compose

```bash
docker compose up --build
```

WAIT A LITTLE )

6) Open your localhost:
   
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


## Структура

- `Dockerfile` — образ для сервиса.
- `docker-compose.yml` — запуск сервиса и PostgreSQL.
- `.env.example` — пример переменных окружения.
- `.env` — рабочая конфигурация для запуска.
- `ai-agent` — исходный код FastAPI.
