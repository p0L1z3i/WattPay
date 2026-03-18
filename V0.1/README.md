# WattPay - Electricity Bill Calculator

A Python-based REST API application for calculating and managing electricity bills for multiple tenants with a PostgreSQL database backend.

## Overview

This application helps property owners and managers calculate electricity bills for different properties and tenants on a monthly basis. It provides a systematic approach to track meter readings, calculate bills, and maintain records of payments.

## Features

- Monthly bill generation
- Multi-tenant support
- Meter reading tracking
- Unit price management
- Detailed bill history

## Tech Stack

### Backend

- **Language:** Python 3.14
- **Framework:** FastAPI 0.128.0
- **Server:** Uvicorn 0.40.0 (ASGI)
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL 18 (via asyncpg)
- **Migrations:** Alembic 1.18.1
- **Validation:** Pydantic
- **Configuration:** INI-based with environment variable overrides

## Architecture

The application follows a layered architecture:

```text
Routes (API Endpoints) → Services (Business Logic) → Models (ORM / Database)
```

- **Routes** define the FastAPI endpoints and handle HTTP requests/responses.
- **Services** contain the business logic and perform database operations via SQLAlchemy async sessions.
- **Models** define the SQLAlchemy ORM entities mapped to PostgreSQL tables.
- **Schemas** provide Pydantic models for request validation and response serialization.

## API Endpoints

### Owner

| Method | Endpoint                                           | Description             |
| ------ | -------------------------------------------------- | ----------------------- |
| GET    | `/owner/get-all-owners`                            | Retrieve all owners     |
| GET    | `/owner/get-owner-by-name/{owner_name}`            | Get owner by name       |
| GET    | `/owner/get-owner-by-contact/{owner_contact}`      | Get owner by contact    |
| POST   | `/owner/add-owner`                                 | Create a new owner      |
| PUT    | `/owner/update-owner/{owner_id}`                   | Full update of an owner |
| PATCH  | `/owner/update-owner/{owner_id}`                   | Update owner contact    |

## Folder Structure for WattPay Application

- wattpay-backend/
  - V0.1/
    - alembic/ — *Database migration scripts (Alembic)*
      - env.py
      - README
      - script.py.mako
      - versions/
    - api/ — *API layer*
      - common/ — *Shared utilities*
        - config_manager.py — *Centralized config with INI parsing and env var overrides*
        - db_session_maker.py — *Async database session factory (singleton)*
        - log/ — *Logging setup*
          - logging.py — *JSON-based logging initialization*
          - conf/
            - logging_config.json — *Log formatters, handlers, and levels*
      - owner/ — *Owner API module*
        - routes.py — *Owner CRUD endpoints*
    - build/
      - logs/ — *Application log output*
    - config/
      - app.ini — *App configuration (database, logging, service settings)*
    - models/ — *SQLAlchemy ORM models*
      - owner.py — *Owner entity mapped to PostgreSQL*
    - schemas/ — *Pydantic validation schemas*
      - owner.py — *Owner request/response models*
    - services/ — *Business logic layer*
      - owner_service.py — *Owner CRUD operations*
    - alembic.ini
    - app.py — *FastAPI application entry point*
    - pyproject.toml
    - README.md
    - .gitignore
    - .python-version
