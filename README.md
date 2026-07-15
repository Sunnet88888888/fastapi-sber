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

# Architecture

> Insert your architecture diagram here.

---

# Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [User Roles](#user-roles)
- [Business Logic](#business-logic)
- [Package Versioning](#package-versioning)
- [AI Workflow](#ai-workflow)
- [API Documentation](#api-documentation)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

# Overview

This project implements the backend infrastructure for an AI-powered document verification system.

| Feature | Description |
|----------|-------------|
| Authentication | JWT Authentication |
| Authorization | RBAC |
| Validation | Parallel document validation |
| Versioning | Immutable package history |
| AI Integration | REST API |
| Database | PostgreSQL |

---

# Features

- JWT Authentication
- Role-Based Access Control (RBAC)
- Parallel document validation
- Immutable package versioning
- AI integration endpoints
- PostgreSQL persistence
- Docker deployment
- Swagger & ReDoc
- Pytest support

---

# Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Programming language |
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

## Clone repository

```bash
git clone https://github.com/Sunnet88888888/fastapi-sber.git
cd fastapi-sber
```

## Configure environment

```bash
touch .env
cp .env.example .env
```

Edit `.env`:

| Variable | Description |
|----------|-------------|
| SECRET_KEY | JWT secret |
| SUPER_USER_SECRET_KEY | Secret used to create administrators |
| DATABASE_URL | PostgreSQL connection string |

## Run

```bash
docker compose up --build
```

## Open

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

# Running Tests

Local:

```bash
../myenv/bin/python -m pytest -vv
```

Docker:

```bash
docker compose run --rm web python -m pytest -vv
```

---

# Project Structure

```text
.
├── ai-agent/
│   ├── app/
│   │   ├── auth/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── db_depends.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── migrations/
│   ├── tests/
│   ├── alembic.ini
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# User Roles

| Role | Description |
|------|-------------|
| Super User | Creates administrators |
| Administrator | Manages users |
| Specialist | Uploads document packages |
| AI Developer | Processes document packages |

> Insert your RBAC diagram and role screenshots here.

---

# Business Logic

> Insert your business workflow diagram here.

## Validation

| Validation | Description |
|------------|-------------|
| File Type | Contract / Invoice / Specification / Act |
| Extension | Allowed extensions |
| Magic Bytes | Binary signature verification |
| Size | Maximum 20 MB |

If validation succeeds, the package status becomes `check_in_progress`.

If validation fails, the package status becomes `rejected`.

---

# Package Versioning

> Insert your package versioning diagram here.

New package:
- Generate UUID
- Create version 1

Existing package:
- Find latest version
- Increment version
- Preserve previous versions

## Document Versioning

Each uploaded document receives its own UUID, ensuring immutable history and independent identification.

---

# AI Workflow

> Insert your AI workflow diagram here.

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/ai/next-unchecked-package | GET | Get next package |
| /api/ai/packages/{package_id}/documents | GET | Download package documents |
| /api/ai/checked_package/{package_id} | POST | Upload AI verification result |

---

# API Documentation

> Insert Swagger screenshot here.

| Documentation | URL |
|--------------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

# Future Improvements

- Background task queue
- Message broker
- Object storage
- Kubernetes deployment
- CI/CD pipeline
- Prometheus & Grafana monitoring

---

# Author

**Sunnet Berdinov**

AI Agent Backend — Technical Assignment.
