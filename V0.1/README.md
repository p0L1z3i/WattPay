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

- **Language:** Python
- **IDE:** Visual Studio Code
- **Database:** PostgreSQL 18
- **Database Management:** pgAdmin 4

## Folder Structure for WattPay Application

- wattpay-backend/
  - V0.1/
    - core/
      - app.ini
      - config.py
      - database.py
    - models/
      - owner.py
      - tenant.py
      - meter.py
    - services/
      - owner_service.py
      - tenant_service.py
      - meter_service.py
    - schemas/
      - owner.py
      - tenant.py
      - meter.py
    - api/
      - owner/
        - routes.py
        - init.py
      - tenant/
        - routes.py
        - init.py
      - meter/
        - routes.py
        - init.py
      - init.py
    - main.py
    - pyproject.toml
    - README.md
    - .gitignore
    - .python-version
