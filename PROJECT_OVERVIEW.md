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
- Odoo conserva el contacto comercial y el presupuesto de Ventas en borrador creados al pulsar «Generar»; PrefWeb sigue siendo la fuente del importe final.
- R2 conserva fotos y resultados cuando `STORAGE_BACKEND=r2`.
- El snapshot de generación evita que un caso cambie a mitad del pipeline.
- La imagen desplegada en Cloud Run, no GitHub por sí solo, determina el código que ejecuta producción.

## Narración eficiente

- Variables por cliente: Gemini redacta las slides 1, 2 y 3; la slide 7 se redacta por código con datos económicos exactos. ElevenLabs produce esos cuatro audios.
- Fijas: slides 4, 5, 6, 8, 9 y 10; texto en `backend/generation/narration/script/fixed.py` y MP3 en `assets/narration/fixed/v4/`. La slide 8 explica la mejora adicional por confirmar el proyecto dentro de los 15 días. Todos estos audios usan la voz de Alberto.
- Los audios fijos solo deben regenerarse si cambia deliberadamente su texto o voz: `PYTHONPATH=. python scripts/generate_fixed_narration_audio.py --force`.
- Las fichas técnicas se añaden una sola vez según PrefWeb: cajón SUMUM Thermoacustic con persiana, Microventilación y UNIK con oscilobatientes, e iSlide con correderas.
- Si hay descuento de cabecera o de línea de ventana, el contexto incluye `discount_applied=true` y la slide 7 garantiza el porcentaje, el precio final y la condición de contratación en los próximos 15 días.
- El montaje añade una cola silenciosa por slide para absorber redondeos de códec y fotogramas.

## Estado comercial y Odoo

La pantalla principal distingue «Sin hacer», «Borrador en curso», «Propuesta generada» y «Enviado al cliente» según el caso, su última generación y el envío registrado. Al generar, se crea o reutiliza el contacto por email y se busca el número estable del presupuesto de PrefWeb en Odoo. Si ya existe, la app solicita confirmar la regeneración: cancelar o sobrescribir las líneas del borrador SmartVitra más reciente. Los documentos enviados, confirmados o gestionados manualmente no se sobrescriben. Un bloqueo por caso impide creaciones simultáneas por varios clics. Se utiliza un único producto técnico de Odoo (`SV-PREFWEB-LINE`) para las líneas; sus descripciones conservan los títulos propios de cada partida. Un descuento de cabecera se añade aparte del descuento de cada línea y se comprueban los totales antes de lanzar la generación. El PDF oficial del presupuesto se descarga mediante el acceso de portal de Odoo y se añade como documento descargable y adjunto del envío; si Odoo no puede producirlo, la propuesta continúa sin ese adjunto. El envío posterior reutiliza el contacto asociado.

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
