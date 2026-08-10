# SmartVitra Commercial Presentation Template

## 1. Purpose

This document defines the canonical structure of the SmartVitra customer
presentation.

The presentation currently consists of 12 slides.

The objective of the automation system is NOT to allow the presentation
generator to freely decide the commercial narrative.

Instead, the system must:

1. preserve the SmartVitra commercial narrative;
2. populate customer-specific information;
3. select the appropriate real customer photographs;
4. use verified technical and commercial information;
5. optionally generate visual simulations of the proposed solution;
6. generate presentation and video content from the same structured source.

The canonical data flow is:

CommercialBrief
    |
    v
PresentationSpec
    |
    +--> Gamma presentation
    |
    +--> VideoScript
    |
    +--> Future visual-generation pipeline

---

# 2. General rules

## 2.1 Fixed versus dynamic content

Slides are classified as:

- FIXED:
  Identical across customer presentations except for global company data that
  may be centrally configured.

- SEMI-DYNAMIC:
  Structure and commercial purpose remain fixed, but customer-specific fields,
  prices, rooms, products, text or imagery change.

- DYNAMIC:
  A substantial part of the content depends on the customer, visit,
  configuration or proposal.

The presentation generator must never independently invent the structure.

---

## 2.2 Data provenance

Customer-specific statements must originate from one of the following:

- Proposal / Odoo data
- PrefWeb data
- visit data
- structured customer needs
- SmartVitra product catalog
- approved SmartVitra commercial configuration
- approved generated content derived from the above

Technical claims must be supported by product documentation.

Commercial claims, guarantees, lead times, promotions and conditions must
come from centrally approved SmartVitra configuration.

The generative layer must not invent:

- performance percentages;
- energy savings;
- acoustic reductions;
- guarantees;
- delivery times;
- discounts;
- promotional gifts;
- market-value increases;
- useful-life claims;
- technical specifications.

---

# 3. Canonical 12-slide presentation

## Slide 01 — Cover

### Type
FIXED

### Current purpose
Brand introduction.

### Current content
- SmartVitra logo
- Comercial de Aluminio y PVC Aspa S.L.

### Dynamic information
None by default.

Potential future optional fields:
- customer name
- proposal number
- proposal date

These must only be added if SmartVitra decides to change the cover design.

### Imagery
SmartVitra corporate branding only.

### AI generation
Not required.

---

## Slide 02 — Current situation

### Canonical title
¿Cómo está tu vivienda?

### Commercial purpose
Demonstrate that SmartVitra understands the problems the customer currently
experiences.

### Type
DYNAMIC

### Current layout
Several problem cards.

Examples currently used:
- Frío en invierno, calor en verano
- Ruido
- Facturas demasiado altas
- Incomodidad diaria

### Dynamic information
Content must be derived from:

CommercialBrief.primary_need
CommercialBrief.secondary_needs

Example:

acoustic_noise
    ->
"Ruido exterior"

thermal_loss
    ->
"Frío, corrientes o pérdida de confort térmico"

### Priority rule
The primary need must receive the strongest visual and narrative emphasis.

Secondary needs may populate the remaining cards.

### Source text
Customer source_text may be used to make the description more personal.

Example:

Customer:
"Lo peor es el ruido de los coches por la noche."

Presentation:
"El ruido del tráfico está afectando al descanso diario en la vivienda."

### Important constraint
Do not introduce additional problems merely to fill the layout.

If only two customer needs are known, prefer two strong cards instead of
inventing four.

### Imagery
Optional real customer photographs associated with the corresponding
problem/opening.

---

## Slide 03 — Consequences of not acting

### Canonical title
¿Qué pasa si no haces nada?

### Commercial purpose
Explain the consequences of leaving the customer's current problem unresolved.

### Type
SEMI-DYNAMIC

### Structure
The visual structure may remain relatively fixed.

### Dynamic information
Text must depend on the actual customer needs.

Examples:

thermal_loss
    ->
continued thermal discomfort

acoustic_noise
    ->
continued noise disturbance and reduced rest

ventilation
    ->
continued ventilation-related discomfort

### Fixed generic concepts
Generic concepts may be centrally approved and reused.

### Claims requiring validation
Statements such as:

- property loses value;
- solution price will necessarily rise;
- energy bills will be reduced by a specific amount;

must not be generated as factual claims without an approved source.

### AI role
AI may adapt approved consequence messages to customer context.

AI must not invent economic or technical consequences.

---

## Slide 04 — Problem confirmation

### Canonical title
¿Este es realmente el problema en tu vivienda?

### Commercial purpose
Create identification between the customer and the problem being described.

### Type
DYNAMIC

### Dynamic information
- primary customer problem;
- optionally one short reinforcing sentence.

### Imagery

Preferred final implementation:

REAL CUSTOMER PHOTO
    |
    v
problem-oriented presentation

For example:
- cold room;
- noisy street-facing opening;
- condensation around window;
- poorly insulated opening.

During early versions, a generic contextual image may be used when a suitable
real photo does not exist.

### Long-term target
The real house should have priority over stock photography.

---

## Slide 05 — Transition to solution

### Canonical title
¿Quieres que te ayudemos a solucionarlo?

### Commercial purpose
Transition from pain/problem narrative to SmartVitra solution.

### Type
FIXED / SEMI-DYNAMIC

### Fixed content
Core title and transition purpose.

### Dynamic content
Normally none.

A very small customer-specific subtitle could be introduced in the future,
but it is not required.

### Imagery
Installation / SmartVitra solution imagery.

Could eventually use company-owned installation photographs.

---

## Slide 06 — Proposed solution

### Canonical title
Nuestra propuesta para tu vivienda

### Commercial purpose
Explain exactly what SmartVitra proposes to install.

### Type
HIGHLY DYNAMIC

### Required data sources
- Proposal.openings
- Proposal.products
- product technical catalog
- glazing configuration
- PrefWeb configuration when available
- services
- customer location if required

### Content

#### Proposed solution
For example:
- PVC window system
- selected profile
- glazing composition
- control solar
- low-emissivity glass
- argon
- warm-edge spacer
- shutter box
- microventilation
- perimeter sealing
- installation finishes

ONLY features actually present in the proposal may be shown.

#### Rooms / openings
The presentation should group openings in a customer-friendly way.

Example:

Dormitorio principal — 2
Salón — 1
Cocina — 1

Total — 4 ventanas

### Technical documentation
Relevant technical documentation may be referenced or attached.

### AI role
AI may translate technical configuration into customer-friendly language.

It must not introduce features that are not present.

---

## Slide 07 — Customer benefits

### Canonical title
Lo que vas a notar desde el primer día

### Commercial purpose
Translate technical characteristics into customer benefits.

### Type
DYNAMIC

### Source
BenefitMatcher result.

Example:

Customer need:
acoustic_noise

Products:
UNIK
THERMOACUSTIC

Matched benefit:
acoustic

Presentation:
Silencio y tranquilidad

### Potential benefits
Only when supported by selected products / configuration:

- thermal comfort
- acoustic comfort
- controlled ventilation
- security
- privacy
- aesthetics
- other catalog-approved benefits

### Critical rule
Do NOT automatically use unsupported numbers.

Examples that require verified evidence:

"Reducción de hasta un 40 % del ruido exterior."

"Hasta un 30 % de reducción en calefacción y aire acondicionado."

Such values must exist as approved structured claims before they can appear.

### AI role
Translate matched benefits into concise customer-oriented language.

---

## Slide 08 — Before / after transformation

### Canonical title
Una decisión cambia todo

### Commercial purpose
Allow the customer to visualize the transformation.

### Type
DYNAMIC

### Strategic target

This is a core future differentiator of the automation.

The desired flow is:

REAL PHOTO OF CUSTOMER HOME
            |
            v
VISUAL GENERATION MODEL
            |
            v
SIMULATION OF SAME SPACE
WITH PROPOSED SMARTVITRA SOLUTION

### BEFORE
Must preferably be:
- an actual photograph taken during the visit.

### AFTER
Future preferred implementation:
- generated from the original customer photograph;
- same room;
- same perspective;
- same structural geometry;
- proposed window solution integrated realistically.

### Important restrictions
Generated images must be marked internally as AI-generated.

They must not be represented internally as photographic evidence of a completed
installation.

### Required metadata
Photo should retain:
- opening_id
- photo_type
- usage
- source photo
- generated/original status
- generation provenance

### Suggested usage values
- current_problem
- before_after
- room_context
- facade
- proposal_visualization

---

## Slide 09 — Why work with SmartVitra

### Canonical title
¿Por qué trabajar con nosotros?

### Type
FIXED

### User decision
This slide is intended to remain identical in all presentations.

### Current content
Examples include:
- Obra limpia y ordenada
- Plazos cumplidos
- Garantía total
- Atención postventa real
- Customer reviews

### Reviews
Current presentation includes customer review excerpts.

### Configuration rule
Although fixed per customer, this information should eventually live in a
central SmartVitra company configuration rather than being duplicated in
presentation-generation code.

### Critical business validation
Before production automation, SmartVitra must confirm the exact approved
wording for:
- warranty duration;
- delivery commitments;
- post-sale commitments;
- review excerpts;
- review source URL.

Once approved, the slide is reused unchanged.

### AI role
None.

---

## Slide 10 — Investment / reference value

### Canonical title
Tu inversión

### Type
SEMI-DYNAMIC

### Commercial purpose
Anchor the value of the proposed installation before displaying the final
customer price.

### Current concept
Reference / market value followed by explanation such as:
"Precio si se comprara ventana a ventana."

### Dynamic fields
Potentially:
- reference value
- standard/list value
- comparison value
- number of windows
- VAT indication

### Data source
Must come from structured pricing.

The presentation generator must NOT calculate or invent a reference value
unless the business rule is explicitly defined.

### Expected architecture

Pricing data
    |
    v
approved pricing rule
    |
    v
Slide 10 reference value

### AI role
None for numbers.

AI may format explanatory wording if required.

---

## Slide 11 — Final price

### Canonical title
Tu precio final

### Type
SEMI-DYNAMIC

### Commercial purpose
Present the actual offer clearly.

### Dynamic fields
- subtotal / final price before VAT depending on company convention
- VAT
- installation inclusion
- payment terms
- discounts
- optional amortization information if supported

### Primary source
Proposal.pricing

### Current examples
- final closed price
- installation included
- no additional costs
- payment schedule

### Amortization table
Current presentation includes an estimated amortization section.

This MUST NOT be generated automatically until SmartVitra provides and
approves the exact calculation methodology and assumptions.

Required future inputs may include:
- estimated annual energy expense
- expected energy reduction
- product useful life
- energy-price assumptions

Without those approved inputs, the amortization section should be omitted or
use only centrally approved static content.

### AI role
No numerical generation.

---

## Slide 12 — Closing / next step

### Canonical title
¿Empezamos?

### Type
FIXED

### User decision
This slide acts as the presentation ending and is reused across customers.

There is no additional separate ending slide.

### Current purpose
Call to action.

### Current content themes
- acceptance incentive
- gifts/promotions
- delivery commitment
- alternative deposit/payment option
- normal payment method
- contact without obligation
- validity period of offer

### Required improvement
The contact section should include centrally configured SmartVitra contact
details.

Suggested fields:
- telephone
- email
- website
- optional WhatsApp
- commercial contact

### Central configuration requirement
Although customer-independent, the following values may change over time and
therefore must NOT be hardcoded permanently into presentation-generation
logic:

- available promotional gifts
- offer-validity period
- extra discount percentage
- delivery times
- compensation for delays
- payment alternatives
- telephone
- email
- website

These values belong to BusinessConfiguration.

### AI role
None.

---

# 4. Dynamic-content matrix

| Slide | Type | Customer-specific | Main source |
|---|---|---:|---|
| 01 Cover | FIXED | No | Brand config |
| 02 Current situation | DYNAMIC | Yes | CustomerNeeds |
| 03 Consequences | SEMI-DYNAMIC | Yes | CustomerNeeds + approved rules |
| 04 Problem confirmation | DYNAMIC | Yes | PrimaryNeed + photos |
| 05 Solution transition | FIXED | No | Template |
| 06 Proposed solution | DYNAMIC | Yes | Proposal + PrefWeb + catalog |
| 07 Benefits | DYNAMIC | Yes | BenefitMatcher |
| 08 Before / After | DYNAMIC | Yes | Visit photos + image generation |
| 09 Why SmartVitra | FIXED | No | BusinessConfiguration |
| 10 Investment | SEMI-DYNAMIC | Yes | Pricing |
| 11 Final price | SEMI-DYNAMIC | Yes | Pricing + payment terms |
| 12 Closing | FIXED | No* | BusinessConfiguration |

*Slide 12 does not vary per customer, but business-level promotions and contact
information may change globally.

---

# 5. Presentation generation architecture

CommercialBrief
        |
        v
PresentationSpecBuilder
        |
        v
PresentationSpec
        |
        +-- slide_01_cover
        +-- slide_02_current_situation
        +-- slide_03_consequences
        +-- slide_04_problem_confirmation
        +-- slide_05_solution_transition
        +-- slide_06_proposal
        +-- slide_07_benefits
        +-- slide_08_before_after
        +-- slide_09_why_smartvitra
        +-- slide_10_investment
        +-- slide_11_final_price
        +-- slide_12_closing
        |
        v
GammaAdapter

Gamma is therefore treated as a renderer/generative presentation engine,
not as the owner of the SmartVitra commercial logic.

---

# 6. Video architecture

The presentation and video must derive from the same structured content.

CommercialBrief
        |
        v
PresentationSpec
        |
        +--------------------+
        |                    |
        v                    v
Gamma presentation       VideoScript
                             |
                             v
                     ElevenLabs / avatar

This avoids inconsistencies between what the customer sees and what the
presenter says.

The video script may include:
- fixed intro blocks;
- fixed SmartVitra explanation blocks;
- customer-specific problem blocks;
- proposal-specific blocks;
- customer-specific pricing blocks;
- fixed closing blocks.

---

# 7. Future real-home visual generation

The target functionality is:

Visit photo
    |
    v
Opening identification
    |
    v
Proposal configuration
    |
    v
Visual generation request
    |
    v
ProposedSolutionImage
    |
    v
Human / automatic validation
    |
    v
Slide 08

Required constraints:

- preserve room geometry;
- preserve camera viewpoint where possible;
- preserve walls, furniture and architectural context;
- change only the relevant window / opening elements;
- use the proposal configuration;
- maintain source-image linkage;
- mark result internally as generated;
- validate output before customer delivery.

The first implementation may be optional and require manual approval.

---

# 8. Presentation QA requirements

Before the presentation can be marked READY_TO_SEND, the system should verify:

- customer name / proposal correct;
- no unknown products;
- no unknown openings;
- every technical claim has an approved source;
- no unsupported numeric claims;
- prices match Proposal;
- VAT presentation is correct;
- payment terms match Proposal;
- customer photographs reference existing openings;
- generated photographs are identified internally;
- uncovered needs are not falsely presented as solved;
- fixed company claims come from approved configuration;
- no unresolved placeholders remain.

---

# 9. Current implementation status

Already implemented:

- Proposal parsing
- pricing extraction
- product catalog
- Proposal enrichment
- CustomerNeeds
- BenefitMatcher
- CommercialBrief
- product technical properties
- services
- photo support in CommercialBrief model

Next implementation blocks:

1. Visit photo ingestion and metadata.
2. BusinessConfiguration.
3. PresentationSpec models.
4. PresentationSpecBuilder for the 12 canonical slides.
5. Gamma API capability research.
6. GammaAdapter.
7. VideoScript.
8. ElevenLabs / avatar integration.
9. Real-home proposed-solution visual generation.
10. Odoo / PrefWeb production integrations.
