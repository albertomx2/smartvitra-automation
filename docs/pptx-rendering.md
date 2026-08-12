# SmartVitra PPTX Rendering Architecture

## 1. Objective

SmartVitra presentations may be rendered deterministically from a PowerPoint
template.

The PPTX renderer is currently the primary implementation candidate while the
Gamma integration remains available as an alternative rendering strategy.

Canonical flow:

CommercialBrief
    |
    v
PresentationSpec
    |
    v
AIContentGenerator
    |
    v
RenderedPresentationContent
    |
    v
PowerPointRenderer
    |
    v
Generated PPTX
    |
    v
PresentationQA
    |
    +---- no issues ----> READY_FOR_REVIEW
    |
    +---- issues --------> Correction Agent
                              |
                              v
                       CorrectionActions
                              |
                              v
                       PowerPointRenderer
                              |
                              v
                       PresentationQA

## 2. Fundamental principle

AI does not directly manipulate PowerPoint internals.

AI decides:

- wording;
- semantic emphasis;
- semantic colors;
- prioritization;
- image selection;
- text shortening;
- corrective actions.

The deterministic PowerPoint renderer executes those decisions.

This separation prevents an AI model from freely moving, deleting or modifying
presentation elements.

## 3. Template contract

Editable PowerPoint shapes use semantic names prefixed with:

sv_

Examples:

sv_s02_title
sv_s02_need_1_title
sv_s02_need_1_body
sv_s02_need_1_border
sv_s08_before_image
sv_s08_after_image
sv_s11_final_price

Production code must reference semantic shape names rather than PowerPoint's
automatic names such as:

Rectangle 5
Text Box 7
Picture 3

## 4. Text rendering

Text must be replaced while preserving the original template style.

The renderer must preserve, whenever present:

- font family;
- font size;
- bold;
- italic;
- underline;
- text color;
- paragraph formatting;
- alignment.

Direct use of:

shape.text = value

must not be used for production dynamic content because it may reconstruct text
runs and alter formatting.

## 5. Text length

The primary strategy for text overflow is controlled generation.

Every dynamic field will eventually have constraints such as:

title:
- maximum characters;
- maximum conceptual lines.

body:
- maximum characters;
- maximum conceptual lines.

Example:

sv_s02_need_1_title:
max_characters = 35

sv_s02_need_1_body:
max_characters = 90

If QA detects that content is too long, the correction agent should request a
shorter equivalent wording.

Font-size reduction is a fallback, not the primary strategy.

## 6. Semantic colors

AI must not directly choose arbitrary RGB values.

AI selects a semantic category.

Initial categories:

problem_high
problem_medium
positive
warning
neutral

The renderer maps those categories to centrally configured SmartVitra colors.

Example:

problem_high
    ->
SmartVitra red

positive
    ->
SmartVitra green

Changing the brand palette must therefore not require changing AI prompts.

## 7. Multi-shape components

Some visual components may be composed of several PowerPoint shapes.

All shapes belonging to the same semantic component must receive compatible
styles.

For example, if a card is composed of:

sv_s02_need_3_border
sv_s02_need_3_accent

both shapes must receive the appropriate semantic style for that card.

The production template should use explicit semantic shape names to avoid
depending on automatic PowerPoint names.

## 8. Presentation agent

The future presentation agent is a controlled correction agent.

It receives:

- PresentationSpec;
- rendered content;
- QA findings;
- allowed actions.

It does NOT receive unrestricted permission to manipulate the PPTX.

Allowed actions initially include:

rewrite_text
set_semantic_color
hide_shape

Future actions may include:

select_image
replace_image
use_alternative_layout
reduce_font_size_within_bounds

Every correction action must be structured and validated before execution.

## 9. Example agent loop

Initial content:

"Las corrientes de aire procedentes de la antigua carpintería producen una
considerable pérdida de confort térmico durante los meses de invierno."

QA:

shape = sv_s02_need_2_body
issue = text_too_long
limit = 90

Correction Agent:

action = rewrite_text
shape = sv_s02_need_2_body
max_characters = 90

AI output:

"En invierno, la vivienda pierde calor y resulta menos confortable."

Renderer:

replace text preserving template style

QA:

PASS

## 10. Images

Image rendering will follow the same deterministic architecture.

PresentationSpec
    |
    v
ImageSelection / AI image generation
    |
    v
approved image asset
    |
    v
PowerPointRenderer
    |
    v
named image shape

The renderer will preserve:

- image frame position;
- width;
- height;
- expected crop / fill behavior.

## 11. Before / after

Slide 08 target flow:

real customer photograph
    |
    v
image generation system
    |
    v
same room with proposed SmartVitra solution
    |
    v
image validation
    |
    v
approved AFTER image
    |
    v
PowerPointRenderer

The PowerPoint renderer itself does not generate images.

## 12. Fixed slides

Slides 01, 05, 09 and 12 remain template-controlled.

They should generally not require AI intervention.

Company-wide information may be populated from BusinessConfiguration where
necessary.

## 13. Dynamic slides

Slides 02, 03, 04, 06, 07, 08, 10 and 11 are populated from structured
application data.

AI may adapt wording only where explicitly allowed.

Numbers such as prices, taxes, discounts and payment terms are rendered
deterministically and must never be generated by AI.

## 14. Renderer strategy

PresentationSpec is renderer-independent.

Supported / planned renderers:

PresentationSpec
    |
    +---- PptxRenderer
    |
    +---- GammaRenderer

PptxRenderer is currently the primary experimental path.

GammaRenderer remains an optional path and can be activated later depending on
SmartVitra's existing subscriptions, desired workflow and generation quality.

## 15. Decision criteria

PPTX rendering is preferred when the priority is:

- deterministic layout;
- exact prices;
- exact images;
- low recurring cost;
- editable final PowerPoint;
- reproducibility.

Gamma remains attractive when the priority is:

- generative layouts;
- rapid visual experimentation;
- existing Gamma subscriptions;
- n8n-based workflows;
- richer generative presentation behavior.

The system architecture must support both without changing PresentationSpec.
