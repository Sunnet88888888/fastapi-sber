# 🤖 AI Agent Backend

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

# 📖 Overview

This project implements the backend infrastructure for an AI-powered document verification system.

The backend is responsible for:

- 🔐 Authentication & Authorization
- 👥 Role management
- 📦 Document package management
- 🗂 Package versioning
- ✅ File validation
- 🤖 AI integration
- 🗄 PostgreSQL storage
- 📄 OpenAPI documentation

---

# ⚙️ Tech Stack

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

# 🚀 Getting Started

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

⏳ Wait until Docker finishes building the containers.

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

# 🧪 Running Tests

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

# 📁 Project Structure

```
.
├── ai-agent/
│   ├── app/
│   │   ├── api/                # REST API endpoints
│   │   ├── application/        # Business logic
│   │   ├── core/               # Configurations, JWT, security
│   │   ├── db/                 # Database layer
│   │   ├── infrastructure/     # Repositories & services
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── main.py             # FastAPI entrypoint
│   │
│   ├── migrations/             # Alembic migrations
│   ├── tests/                  # Unit & integration tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 🔐 User Roles

The system implements **Role-Based Access Control (RBAC)** with four permission levels.

---

## 👑 Super User

The highest privilege level.

Permissions:

- Create administrators
- Uses `SUPER_USER_SECRET_KEY`
- Distributes administrator credentials

---

## 🛡 Administrator

Responsible for managing operational users.

Permissions:

- Create Specialists
- Create AI Developers
- Manage user accounts
- Distribute login credentials

---

## 📄 Specialist

Responsible for uploading document packages.

Permissions:

- Upload packages
- Create new package versions
- View processing status

---

## 🤖 AI Developer

Dedicated service role used by the AI agent.

Permissions:

- Retrieve packages waiting for processing
- Download package documents
- Submit AI verification results

---

# 🧠 Business Logic

The verification pipeline follows several sequential stages.

```text
Upload Package
       │
       ▼
Save Package
(UUID + Database)
       │
       ▼
Parallel Validation
 ├── File type
 ├── File extension
 └── Size ≤ 20 MB
       │
       ▼
 ┌───────────────┐
 │ Validation OK │
 └──────┬────────┘
        │
        ▼
check_in_progress
        │
        ▼
AI Agent requests next package
        │
        ▼
Downloads package documents
        │
        ▼
Processes documents
        │
        ▼
POST verification result
        │
        ▼
approved / rejected
```

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

# 📦 Package Versioning

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

Example:

```
Package
│
├── Version 1
├── Version 2
├── Version 3
└── Version 4
```

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

# 🔄 AI Workflow

The AI service communicates through three endpoints.

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

# 📚 API Documentation

After starting the application:

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

# 📄 License

This project was developed as part of the AI Agent Backend technical assignment.
