
# AI Agent Backend

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Alembic-4B8BBE?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
</p>

<p align="center">
Backend service for automated document verification before submission to a bank using AI.
</p>

---

# Overview

This project implements the backend infrastructure for an AI-powered document verification system.

The backend is responsible for:

- Authentication & Authorization
- Role management
- Document package management
- Package versioning
- File validation
- AI integration endpoints
- PostgreSQL storage
- OpenAPI documentation

---

# Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming language |
| FastAPI | REST API |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| Argon2 | Password hashing |
| JWT | Authentication |
| Docker | Containerization |
| Docker Compose | Local deployment |

---

# Getting Started

## 1. Clone repository

```bash
git clone https://github.com/Sunnet88888888/fastapi-sber.git
```

---

## 2. Enter project directory

```bash
cd fastapi-sber
```

---

## 3. Create environment file

```bash
touch .env
cp .env.example .env
```

---

## 4. Configure environment variables

Open `.env` and change the secret values.

<img width="624" height="109" alt="env" src="https://github.com/user-attachments/assets/6a8f72ec-a77c-4dde-a012-81341b135c0d" />

### Environment variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Secret used for JWT authentication |
| `SUPER_USER_SECRET_KEY` | Secret key required to create administrators |
| `DATABASE_URL` | PostgreSQL connection string |

> **Note:** The project already runs PostgreSQL inside Docker, so changing `DATABASE_URL` is optional.

---

## 5. Start application

```bash
docker compose up --build
```

 Wait until Docker finishes building the containers.

---

## 6. Open application

Application

```
http://localhost:8000
```

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# Running Tests

### Locally

```bash
cd /Users/sunnet/Desktop/ai-agent-sber/ai-agent

../myenv/bin/python -m pytest -vv
```

### Inside Docker

```bash
docker compose run --rm web python -m pytest -vv
```

---

# Project Structure
```text
.
├── ai-agent/
│   ├── app/
│   │   ├── auth/               # Authentication & authorization
│   │   ├── models/             # SQLAlchemy models
│   │   ├── repositories/       # Database access layer
│   │   ├── routers/            # FastAPI API endpoints
│   │   ├── services/           # Business logic
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database connection
│   │   ├── db_depends.py       # Database dependencies
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── main.py             # FastAPI application entrypoint
│   │
│   ├── migrations/             # Alembic migrations
│   ├── tests/                  # Unit & integration tests
│   ├── alembic.ini             # Alembic configuration
│   └── requirements.txt        # Project dependencies
│
├── docker-compose.yml          # Docker services configuration
├── .env.example                # Environment variables example
└── README.md                   # Project documentation
```

---

# User Roles

The system implements **Role-Based Access Control (RBAC)** with four permission levels.


<img width="974" height="389" alt="Снимок экрана 2026-07-15 в 09 46 43" src="https://github.com/user-attachments/assets/3997e9fb-96ab-445c-8e58-8b98494147da" />






---

## Super User

The highest privilege level.

<img width="785" height="573" alt="Снимок экрана 2026-07-15 в 09 38 28" src="https://github.com/user-attachments/assets/4dbf15d8-c6c9-4da7-9bab-47a2e1d42172" />


Permissions:

- Create administrators
- Uses `SUPER_USER_SECRET_KEY`
- Distributes administrator credentials

---

## Administrator

Responsible for managing operational users.


<img width="530" height="497" alt="Снимок экрана 2026-07-15 в 09 39 12" src="https://github.com/user-attachments/assets/e7c1f993-77be-4a7e-a39d-d7cee6116661" />

Permissions:

- Create Specialists
- Create AI Developers
- Manage user accounts
- Distribute login credentials

---

## Specialist
<img width="692" height="562" alt="Снимок экрана 2026-07-15 в 09 39 52" src="https://github.com/user-attachments/assets/ab8834ad-7d2a-4239-9bca-6afe574405ed" />

Responsible for uploading document packages.

Permissions:

- Upload packages
- Create new package versions
- View processing status

---

## AI Developer

Dedicated service role used by the AI agent.

<img width="638" height="583" alt="Снимок экрана 2026-07-15 в 09 43 24" src="https://github.com/user-attachments/assets/3317f109-dd84-4faf-920f-b47847c8762c" />


Permissions:

- Retrieve packages waiting for processing
- Download package documents
- Submit AI verification results

---

# Business Logic

The verification pipeline follows several sequential stages.

<img width="1079" height="769" alt="Снимок экрана 2026-07-15 в 09 31 10" src="https://github.com/user-attachments/assets/70dedcb6-1261-475b-b6d4-a2bf76d00038" />


---

## Validation

Every uploaded document is validated before reaching the AI.

Checks include:

- Supported document type
- File extension
- Magic bytes verification
- Maximum size of **20 MB**

If validation fails:

- package status becomes `rejected`
- error details are returned
- AI agent never receives the package

Otherwise:

- package status becomes `check_in_progress`

---

# Package Versioning

The system supports immutable document package versioning.

## New Package

If no `package_id` is provided:

- Generate new UUID
- Create Package
- Set version = **1**

---

## Existing Package

If `package_id` exists:

- Find latest package version
- Increment version number
- Save a completely new package version

<img width="1144" height="765" alt="Снимок экрана 2026-07-15 в 09 32 58" src="https://github.com/user-attachments/assets/d4e025f5-b5ee-455a-8b58-720e14bce216" />


No previous versions are removed.

---

## Document Versioning

Each uploaded document receives its own UUID.

```
Package
│
├── Version 1
│     ├── UUID
│     ├── UUID
│     └── UUID
│
├── Version 2
│     ├── UUID
│     ├── UUID
│     └── UUID
```

This guarantees:

- immutable history
- independent document identification
- complete audit trail

---

# AI Workflow

The AI service communicates through three endpoints.

<img width="674" height="628" alt="Снимок экрана 2026-07-15 в 09 33 58" src="https://github.com/user-attachments/assets/9493dbe1-7f03-415a-8d45-25e7ed84666c" />

### Get next package

```
GET /api/ai/next-unchecked-package
```

Returns the next package waiting for processing.

---

### Download package documents

```
GET /api/ai/packages/{package_id}/documents
```

Returns every document belonging to the selected package.

---

### Send verification result

```
POST /api/ai/checked_package/{package_id}
```

After processing, the AI sends:

- verification status
- detected issues
- explanation

The backend updates the package status to:

- ✅ approved
- ❌ rejected

---

# 
API Documentation

After starting the application:


<img width="1209" height="868" alt="Снимок экрана 2026-07-15 в 09 34 55" src="https://github.com/user-attachments/assets/3789879c-fcaa-4a74-b9f4-f75fd64bf026" />

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 🐳 Docker

The project is fully containerized.

Services include:

- FastAPI
- PostgreSQL

Start everything with:

```bash
docker compose up --build
```

---

# License

This project was developed by Berdinov Sunnet.
