# SmartVitra Automation: guía general

## Propósito

SmartVitra transforma un presupuesto técnico y la información recogida durante una visita en una propuesta comercial personalizada: presentación PowerPoint, guion, narración y vídeo. La aplicación conserva el caso, permite revisar los resultados y soporta su posterior entrega al cliente.

## Directorios importantes

- `backend/api`: aplicación FastAPI, autenticación y endpoints.
- `backend/cases`: casos comerciales, necesidades y datos de visita.
- `backend/integrations/prefweb`: login, consultas, parsing y normalización de PrefWeb.
- `backend/generation`: snapshot, contexto, orquestación, narración, vídeo y artefactos.
- `backend/presentation` y `backend/rendering/pptx`: contenido y render de la plantilla PowerPoint.
- `backend/storage`: almacenamiento local o Cloudflare R2.
- `frontend`: SPA React/Vite servida por FastAPI en producción.
- `alembic`: migraciones PostgreSQL.
- `assets`: plantilla, imágenes y audios fijos versionados.
- `tests`: pruebas automatizadas.

## Fuentes de verdad

- PrefWeb es la fuente de los datos técnicos, cliente y precios. Para totales con descuento debe usarse el resumen exacto del documento, no la suma de líneas.
- PostgreSQL conserva casos, trabajos, estados, artefactos y entregas.
- R2 conserva fotos y resultados cuando `STORAGE_BACKEND=r2`.
- El snapshot de generación evita que un caso cambie a mitad del pipeline.
- La imagen desplegada en Cloud Run, no GitHub por sí solo, determina el código que ejecuta producción.

## Narración eficiente

- Variables por cliente: slides 1, 2, 3 y 7; Gemini redacta el texto y ElevenLabs produce cuatro audios.
- Fijas: slides 4, 5, 6, 8 y 9; texto en `backend/generation/narration/script/fixed.py` y MP3 en `assets/narration/fixed/v1/`.
- Los audios fijos solo deben regenerarse si cambia deliberadamente su texto o voz: `PYTHONPATH=. python scripts/generate_fixed_narration_audio.py --force`.
- Si hay descuento, el contexto incluye `discount_applied=true` y la slide 7 garantiza el mensaje del precio final condicionado a contratación en los próximos 15 días.
- El montaje añade una cola silenciosa por slide para absorber redondeos de códec y fotogramas.

## Desarrollo y validación

```bash
cd /Users/albertomartinezmendez/AlbertoDir/smartvitra-automation
source .venv/bin/activate

black backend tests
ruff check backend tests --fix
mypy backend
pytest

cd frontend
npm run build
cd ..
```

Antes de formatear o añadir archivos, revisar `git status` y `git diff`: el árbol de trabajo puede contener cambios del usuario que deben conservarse.

## Git y producción

```bash
git add <archivos revisados>
git commit -m "Describe el cambio"
git push origin develop

PROJECT_ID="project-c165bbbb-9f62-48fc-ba9"
REGION="europe-west3"
TAG="una-version-unica"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/smartvitra/app:$TAG"

gcloud builds submit --project="$PROJECT_ID" --tag="$IMAGE" .
gcloud run services update smartvitra-web \
  --project="$PROJECT_ID" --region="$REGION" --image="$IMAGE"
gcloud run jobs update smartvitra-generation \
  --project="$PROJECT_ID" --region="$REGION" --image="$IMAGE"
```

Verificar después que web y job referencian la misma imagen, consultar `/health` y hacer una prueba funcional real desde la aplicación.
