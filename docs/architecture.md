# Architecture

## Objetivo

Definir la arquitectura técnica de SmartVitra Automation.

## Principios

- Cloud first
- Trazabilidad
- Datos críticos deterministas
- IA limitada a tareas semánticas
- Integraciones desacopladas
- Revisión humana antes del envío

## Componentes

Pendiente de definir.

## Product Catalog

The technical product catalog is dynamically loaded from:

`assets/catalog/<product>/product.json`

Each product directory contains:

- `product.json`: structured product metadata.
- `source.pdf`: original technical documentation.
- `images/`: optional visual assets in future versions.

Products must not be hardcoded into application code.

`ProductCatalogRepository` rejects duplicate product codes.

The original technical document remains the source of truth for technical product data.

## Commercial presentation

The canonical SmartVitra customer presentation is defined in:

`docs/presentation-template.md`

Presentation-generation integrations must follow this specification.

The presentation structure is controlled by the application through a
`PresentationSpec`; external generative tools must not independently determine
the SmartVitra commercial narrative.

## Presentation rendering strategies

`PresentationSpec` is renderer-independent.

Current architecture:

CommercialBrief
    |
    v
PresentationSpec
    |
    +-----------------------+
    |                       |
    v                       v
PptxRenderer           GammaRenderer
    |                       |
    v                       v
PowerPoint             Gamma presentation

The current primary implementation experiment is `PptxRenderer` because the
SmartVitra commercial presentation has a strongly standardized 12-slide
structure.

Gamma remains an optional rendering strategy.

### AI presentation layer

AI is placed before and after deterministic rendering where useful:

PresentationSpec
    |
    v
AIContentGenerator
    |
    v
PptxRenderer
    |
    v
PresentationQA
    |
    v
CorrectionAgent
    |
    v
validated correction actions

The AI agent must not manipulate arbitrary PowerPoint XML or freely modify the
layout.

See:

`docs/pptx-rendering.md`
