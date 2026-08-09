# SmartVitra Automation

Plataforma de automatización del proceso comercial de SmartVitra.

## Objetivo

Automatizar el flujo desde la configuración técnica del presupuesto hasta la generación y entrega de la propuesta comercial.

## Arquitectura prevista

PrefWeb / Odoo / Fotos
        ↓
Modelo normalizado Proposal
        ↓
Enriquecimiento técnico y comercial
        ↓
Gamma
        ↓
QA automático
        ↓
Guion y vídeo
        ↓
Odoo
        ↓
Revisión humana y envío

## Stack inicial

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker
- pytest

## Estado

Fase inicial de arquitectura y modelado de datos.
