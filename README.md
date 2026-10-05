# SmartVitra Automation

Prototipo de arquitectura para automatizar propuestas comerciales: transformar información técnica de pedidos en una propuesta estructurada, enriquecerla y preparar materiales para revisión humana.

## Estado real

El repositorio contiene carpetas de dominio, API, integraciones y validadores, documentación y expedientes de referencia. **Todavía no incluye un servidor FastAPI ejecutable ni un flujo comercial completo.** PrefWeb, Odoo, Gamma y generación de vídeo forman parte del diseño, no de una integración lista para usar.

## Arquitectura y contenido

- `backend/domain`: ubicación prevista para el modelo Proposal.
- `backend/api`, `services`, `validators`, `workers`: estructura inicial.
- `backend/integrations`: adaptadores previstos para sistemas externos.
- `docs`: decisiones y especificaciones.
- `tests/cases`: expedientes de validación; no equivalen a pruebas automatizadas.
- `docker-compose.yml`: únicamente PostgreSQL 16.

## Preparar el entorno

Necesitas Python 3.12 y Docker Compose.

```bash
git clone https://github.com/albertomx2/smartvitra-automation.git
cd smartvitra-automation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose config --quiet
docker compose up -d postgres
docker compose ps
```

En Windows activa el entorno con `.venv\Scripts\Activate.ps1`. PostgreSQL escucha en el puerto 5432. No hay página web, endpoint de salud ni comando de arranque de API en esta revisión. Si el puerto está ocupado, cambia el puerto del host en Compose.

**La contraseña incluida en Compose es solo de desarrollo.** Cambia credenciales y limita el puerto a localhost antes de trabajar con documentos reales. `docker compose down` para los contenedores; `down -v` elimina la base.

## Validación y siguientes pasos

Revisar los casos y el modelo descrito en `docs`; implementar después parsers, contratos, API y pruebas. `python -m pytest` permite detectar pruebas futuras, pero puede terminar sin tests recopilados en esta estructura inicial. No se ha validado aquí un flujo extremo a extremo.

No subir documentos de clientes, secretos de proveedores ni exportaciones de Odoo. Hay expedientes descritos como reales: revisar permisos y anonimización antes de reutilizarlos o distribuirlos. Este repositorio no es un servicio de producción ni garantiza exactitud de presupuestos.
