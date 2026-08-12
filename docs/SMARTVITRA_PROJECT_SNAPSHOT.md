# SmartVitra Automation — Estado actual del proyecto

## Objetivo de este documento

Este archivo sirve como snapshot temporal del estado actual del proyecto antes de comenzar la integración con PrefWeb.

No pretende sustituir la documentación existente en `docs/`. Más adelante se podrá consolidar junto con `README.md`, `architecture.md`, `workflow.md`, `todo.md` y el resto de documentación técnica.

---

# 1. Estado general

Actualmente existe un pipeline funcional para generar propuestas comerciales de SmartVitra en PowerPoint a partir de:

- datos estructurados del cliente y del presupuesto;
- contenido comercial generado con Gemini;
- iconos dinámicos;
- fotografías dinámicas;
- fotografía automática de fachada mediante Google Maps Platform;
- datos deterministas como nombre, dirección, fechas, número de presupuesto, precio y forma de pago.

La siguiente fase del proyecto es estudiar e integrar PrefWeb.

Después de PrefWeb se definirá la aplicación para el comercial y, posteriormente, la generación de imágenes mediante IA.

---

# 2. Plantilla PowerPoint actual

La plantilla principal actual es:

`experiments/pptx_template/input/template.pptx`

La plantilla anterior se conserva para referencia y reutilización de código.

La presentación actual tiene 7 diapositivas.

Se han renombrado los elementos dinámicos mediante nombres estables del tipo:

- `sv_s01_cover_photo`
- `sv_s01_intro_text`
- `sv_s01_customer_name`
- `sv_s01_address`
- `sv_s01_proposal_number`
- `sv_s01_date`
- `sv_s02_problem_photo`
- `sv_s02_issue_1`
- `sv_s02_issue_2`
- `sv_s02_issue_3`
- `sv_s02_issue_4`
- `sv_s02_issue_5`
- `sv_s02_issue_6`
- `sv_s03_generated_solution_image`
- `sv_s03_solution_1`
- `sv_s03_solution_1_icon`
- `sv_s03_main_benefit`
- `sv_s03_main_benefit_secondary`
- `sv_s03_benefit_claim`
- `sv_s05_project_photo_1`
- `sv_s05_project_photo_2`
- `sv_s05_project_photo_3`
- `sv_s07_generated_result_image`
- `sv_s07_project_summary`
- `sv_s07_budget_block`

El renderer modifica solo los elementos dinámicos y preserva la plantilla original:

- posiciones;
- tamaños;
- tipografías;
- estilos;
- colores;
- geometría;
- distribución visual.

---

# 3. Slide 1 — Portada

Contenido dinámico:

- texto introductorio;
- nombre del cliente;
- dirección;
- número de presupuesto;
- fecha;
- fotografía de la fachada.

El título y elementos de branding permanecen fijos.

## Fachada automática

La fotografía de portada ya puede obtenerse automáticamente mediante Google Maps Platform.

Flujo validado:

```text
Dirección del cliente
        |
        v
Geocoding API
        |
        v
Coordenadas del inmueble
        |
        v
Street View metadata
        |
        v
Panorama cercano
        |
        v
Cálculo del heading
cámara -> inmueble
        |
        v
Street View Static API
        |
        v
Fotografía orientada hacia la fachada
        |
        v
sv_s01_cover_photo
```

La prueba realizada con una dirección real funcionó correctamente.

Integración implementada en:

`backend/integrations/google_maps/street_view.py`

Variable de entorno:

`GOOGLE_MAPS_API_KEY`

La clave no debe versionarse.

---

# 4. Slide 2 — Lo que hemos detectado

La fotografía será aportada en el futuro por el comercial.

Gemini genera:

- 5 problemas / aspectos detectados;
- 1 frase final de impacto.

Cada problema se estructura como:

```text
keyword
detail
```

Ejemplo:

```text
RUIDO EXTERIOR
afecta al descanso
```

La keyword conserva el estilo destacado de la plantilla.

La frase final utiliza un tratamiento visual más llamativo y rojo.

Ejemplos de tono:

- `CALOR INSOPORTABLE`
- `MUCHO RUIDO A DIARIO`
- `DERROCHE DE DINERO`

El renderer controla su disposición para evitar que el texto salga de la diapositiva.

---

# 5. Slide 3 — Nuestra propuesta

Gemini genera entre 1 y 6 soluciones según los datos disponibles.

Cada solución contiene:

```text
text
icon_key
```

Los iconos son dinámicos.

Catálogo actual de categorías:

- thermal
- acoustic
- energy
- solar_control
- daylight
- ventilation
- air_tightness
- security
- privacy
- durability
- maintenance
- home_value
- aesthetics
- comfort
- humidity
- weather_protection

También se generan:

- beneficio principal;
- beneficio secundario;
- claim comercial.

El layout puede redistribuir las soluciones cuando no existen las 6 para evitar grandes huecos visuales.

La imagen principal de esta slide está prevista para ser generada mediante IA en una fase posterior.

---

# 6. Slide 4

Slide esencialmente fija.

No forma parte actualmente del contenido generado por Gemini.

---

# 7. Slide 5 — Proyectos similares

Tiene tres fotografías.

Actualmente se utilizan imágenes de prueba.

En el futuro las fotografías podrán proceder de:

- la aplicación del comercial;
- una base de datos de proyectos anteriores;
- una selección automática de proyectos similares.

La estrategia definitiva se decidirá después de PrefWeb y de definir la aplicación.

---

# 8. Slide 6

Contenido fijo.

Actualmente no requiere generación dinámica.

---

# 9. Slide 7 — Propuesta final

Contenido dinámico:

- resumen del proyecto;
- presupuesto;
- fecha de validez;
- forma de pago;
- imagen final del resultado propuesto.

Gemini genera únicamente el resumen comercial del proyecto.

Los siguientes campos son deterministas y no deben ser decididos por Gemini:

- importe;
- fecha;
- validez;
- forma de pago.

La fecha se muestra en el bloque:

`IVA incluido · Válido hasta DD/MM/AA`

La forma de pago también se mantiene como dato estructurado para poder modificarla en el futuro si PrefWeb proporciona condiciones diferentes.

La imagen principal está prevista para ser generada mediante IA.

---

# 10. Gemini

Se utiliza:

`GeminiStructuredClient`

Gemini trabaja mediante salida estructurada con Pydantic.

El pipeline actual incluye:

```text
Datos reales
   |
   v
Gemini
   |
   v
Modelo Pydantic
   |
   v
Normalizer
   |
   v
Validator
   |
   +------ válido ------> Renderer
   |
   +------ inválido ----> Corrector Gemini
                              |
                              v
                        nueva validación
```

Existe un máximo de intentos de corrección para evitar loops indefinidos.

---

# 11. Separación entre IA y datos deterministas

Gemini no controla:

- nombre del cliente;
- dirección;
- número de presupuesto;
- fecha;
- precio;
- fecha de validez;
- forma de pago.

Estos datos se insertan de manera determinista.

Gemini sí controla principalmente:

- introducción comercial;
- problemas detectados;
- frase de impacto;
- soluciones propuestas;
- beneficios;
- claims;
- resumen comercial del proyecto;
- selección de iconos permitidos.

Esta separación evita que el LLM modifique información contractual o financiera.

---

# 12. Control de longitud y render

Restricciones específicas de la plantilla:

`backend/presentation/content/template_v2_constraints.py`

Existe:

- normalización;
- validación;
- corrección automática;
- preservación de estilo de PowerPoint;
- tratamiento especial de keywords;
- tratamiento especial de la frase roja de impacto;
- redistribución de soluciones;
- sustitución de imágenes;
- sustitución de iconos.

Se corrigieron problemas observados durante las pruebas como:

- textos truncados;
- frases terminadas en `con.`, `para.`, etc.;
- keywords colocadas después del detalle;
- huecos visuales grandes;
- textos fuera de la diapositiva;
- geometrías alteradas;
- iconos no sustituidos correctamente.

---

# 13. Iconos

Los iconos dinámicos están almacenados en:

`assets/presentation/icons/benefits/`

El renderer selecciona el recurso correspondiente según `icon_key`.

La geometría del placeholder original se mantiene.

---

# 14. Fotografías del comercial — pendiente

Esta es una de las siguientes piezas importantes, pero se desarrollará después de estudiar PrefWeb.

La aplicación del comercial probablemente permitirá:

- seleccionar proyecto;
- indicar estancia;
- subir una o varias fotografías;
- añadir notas;
- incluir otros datos que se determinen posteriormente.

Modelo conceptual provisional:

```text
room
photos[]
notes
```

No debe cerrarse todavía el schema.

Primero hay que conocer qué información ofrece PrefWeb para evitar pedir al comercial datos duplicados.

---

# 15. Imágenes generadas mediante IA — pendiente

Una vez disponibles:

1. datos reales de PrefWeb;
2. fotografías reales del comercial;

se abordará la generación o edición de imágenes mediante IA.

Casos principales previstos:

## Slide 3

Generar una visualización de la solución técnica propuesta.

## Slide 7

Generar una imagen aproximada de cómo quedaría la vivienda con la propuesta SmartVitra.

La implementación debe utilizar datos reales de:

- tipo de ventana;
- número de hojas;
- colores;
- perfiles;
- vidrio;
- configuración;
- fotografía real de la estancia / hueco.

No se desarrollará esta fase antes de disponer de PrefWeb y de definir la entrada de fotografías.

---

# 16. Aplicación del comercial — orden previsto

La aplicación se hará después de PrefWeb.

Motivo:

PrefWeb probablemente ya contendrá parte de la información necesaria.

La aplicación debe pedir únicamente datos adicionales.

Flujo objetivo:

```text
PrefWeb
   |
   v
Modelo de proyecto
   ^
   |
App comercial
(fotos + notas + datos adicionales)
```

Ambas fuentes deben alimentar un mismo modelo de dominio.

---

# 17. Próxima fase — PrefWeb

PrefWeb es la siguiente prioridad.

Antes de programar hay que estudiar en detalle lo aprendido en la reunión con la empresa.

Objetivos:

1. entender cómo acceder a PrefWeb;
2. conocer endpoints, autenticación y estructura;
3. determinar qué datos devuelve;
4. identificar cliente;
5. identificar dirección;
6. identificar presupuesto;
7. identificar productos;
8. identificar huecos / ventanas;
9. identificar dimensiones;
10. identificar vidrios;
11. identificar configuración y equipamiento;
12. identificar servicios;
13. identificar precios;
14. identificar descuentos;
15. identificar condiciones de pago;
16. determinar qué datos faltan;
17. construir un modelo estable que alimente presentación y futura app.

---

# 18. Arquitectura objetivo

```text
                        PREFWEB
                           |
                           v
                    Modelo de proyecto
                           ^
                           |
                 App del comercial
             fotos / notas / contexto
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
        Gemini        Google Maps       Imagen IA
        textos          fachada          renders
        iconos
           |               |               |
           +---------------+---------------+
                           |
                           v
                   Renderer PowerPoint
                           |
                           v
                   Presentación final
```

---

# 19. Calidad y tests

Antes de crear un checkpoint:

```bash
ruff check backend tests scripts experiments
black --check backend tests scripts experiments
mypy backend
pytest -q
```

En el último checkpoint previo a este documento el proyecto tenía todos los tests pasando.

Los tests cubren actualmente distintas partes como:

- modelos;
- parsing;
- normalización;
- presentación;
- render PPTX;
- preservación de estilos;
- sustitución de imágenes;
- sustitución de iconos;
- layout;
- generator;
- integración estructurada;
- heading de Street View.

---

# 20. Seguridad

Nunca se deben versionar:

- `.env`;
- API keys;
- tokens;
- credenciales;
- secretos;
- imágenes temporales descargadas.

Variables sensibles actuales:

- `GEMINI_API_KEY`
- `GOOGLE_MAPS_API_KEY`

Los archivos temporales se guardan bajo:

`tmp/`

`tmp/` debe permanecer en `.gitignore`.

---

# 21. Estado de las imágenes

Actualmente:

| Elemento | Estado |
|---|---|
| Slide 1 — fachada | Google Street View funcionando |
| Slide 2 — foto problema | Pendiente app comercial |
| Slide 3 — imagen propuesta | Pendiente IA |
| Slide 5 — proyectos similares | Pendiente estrategia/app/DB |
| Slide 7 — resultado propuesto | Pendiente IA |

---

# 22. Orden de trabajo desde este checkpoint

1. Guardar este estado en Git.
2. Subir checkpoint a GitHub.
3. Estudiar PrefWeb en detalle.
4. Implementar integración PrefWeb.
5. Construir / adaptar el modelo de dominio.
6. Determinar qué datos faltan después de PrefWeb.
7. Diseñar aplicación del comercial.
8. Implementar subida y asociación de fotografías.
9. Implementar imágenes generadas/editadas mediante IA.
10. Integrar todas las fuentes en el pipeline final.
11. Revisar y consolidar documentación del proyecto.
12. Crear un `README.md` definitivo cuando la arquitectura esté estabilizada.

---

# 23. Principio de diseño actual

El objetivo no es hacer una presentación rígida con textos reemplazados.

El objetivo es construir un sistema donde:

- los datos contractuales sean deterministas;
- Gemini redacte únicamente contenido comercial;
- las fotografías reales procedan de fuentes controladas;
- las imágenes generadas se basen en datos reales;
- Google Maps resuelva automáticamente la fachada cuando sea posible;
- la plantilla PowerPoint mantenga exactamente su diseño;
- la presentación se genere automáticamente a partir de PrefWeb + datos adicionales del comercial.
