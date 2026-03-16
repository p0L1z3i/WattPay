# Electricity Bill Calculator

A Python-based application for calculating and managing electricity bills for multiple tenants with a PostgreSQL database backend.

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

- **Coding Language:** Python
- **Database:** PostgreSQL 18

## Folder Structure for WattPay Application

- wattpay-backend/
  - V0.1/
    - alembic/
      - env.py
      - README
      - script.py.mako
      - versions/
    - api/
      - common/
        - config_manager.py
        - db_session_maker.py
        - log/
          - logging.py
          - conf/
            - logging_config.json
      - owner/
        - routes.py
    - build/
      - logs/
    - config/
      - app.ini
    - models/
      - owner.py
    - schemas/
      - owner.py
    - services/
      - owner_service.py
    - alembic.ini
    - app.py
    - pyproject.toml
    - README.md
    - .gitignore
    - .python-version
