# Medical Records Transfer Microservice

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

A secure, high-performance microservice for transferring medical records between healthcare organizations with HIPAA-compliant auditing.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)  
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
- [Development](#development)
  - [Testing](#testing)
  - [Code Quality](#code-quality)
  - [Migrations](#migrations)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [Kubernetes](#kubernetes)
  - [AWS ECS](#aws-ecs)
- [Monitoring](#monitoring)
- [License](#license)
- [Contact](#contact)

## Features

### Core Functionality
- 🔒 End-to-end encrypted record transfers
- 🏥 FHIR/HL7 standards compliance
- 📊 Real-time transfer monitoring
- ♻️ Automatic retry mechanism

### Supported Data Formats
| Format | Version | Default |
|--------|---------|---------|
| FHIR   | 4.0.1   | ✓       | 
| HL7    | 2.5     |         |
| JSON   | 1.2     |         |

## Architecture

```mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[MedicalRecordService]
    C --> D[AuthService]
    C --> E[ExportService]
    C --> F[ImportService]
    E --> G[(PostgreSQL)]
    F --> G
    E --> H[External EHR]
    C --> I[Redis]
    I --> J[Celery Workers]
