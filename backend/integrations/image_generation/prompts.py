from __future__ import annotations

from backend.generation.snapshot import (
    GenerationWindowSnapshot,
)


def build_solution_image_prompt(
    *,
    window: GenerationWindowSnapshot,
) -> str:
    problem_guidance = {
        "noise": (
            "Make the acoustic benefit visually understandable. "
            "When appropriate for the room, include one secondary person "
            "reading, studying, working, resting or enjoying the space "
            "peacefully near the renovated window. The activity should "
            "naturally suggest concentration, rest and freedom from disturbing "
            "exterior noise. The person must not obscure the window."
        ),
        "thermal": (
            "Make thermal comfort visually understandable. "
            "When appropriate, include one secondary person comfortably using "
            "the room in normal indoor clothing, relaxed and clearly enjoying "
            "a pleasant indoor climate. Use attractive natural light and a "
            "comfortable atmosphere. Do not use exaggerated signs of heat or "
            "cold and do not make heaters, fans or air conditioners the story."
        ),
        "air": (
            "Make the absence of drafts and air infiltration visually "
            "understandable. When appropriate, show one secondary person "
            "comfortably using the area close to the renovated window. "
            "Curtains, lightweight fabrics and nearby objects should appear "
            "naturally still, creating a subtle feeling of a stable and "
            "comfortable interior environment."
        ),
        "security": (
            "Communicate safety primarily through the renovated closure: "
            "a solid, professionally installed and reassuring window. "
            "A person may appear naturally in the room, but do not rely on "
            "people, locks, weapons or exaggerated security imagery to "
            "communicate the benefit."
        ),
        "aesthetic": (
            "Make the architectural improvement itself the visual story. "
            "Emphasize the clean integration, proportions, finish, natural "
            "light and overall visual quality of the renovated window. "
            "A person is normally unnecessary unless they genuinely improve "
            "the composition."
        ),
        "other": (
            "Translate the customer's stated need into a subtle, believable "
            "visual story. A secondary person may be included when a natural "
            "human activity makes the benefit easier to understand."
        ),
    }

    problem = problem_guidance.get(
        window.problem_type or "",
        (
            "Present the renovation as a meaningful improvement to the comfort "
            "and quality of the customer's real home."
        ),
    )

    return f"""
Create a photorealistic, aspirational AFTER photograph of
a real residential window renovation.

You are not required to reproduce INPUT IMAGE 1
pixel-for-pixel.

The objective is to transform the real customer photograph
into a polished professional architectural/interior
photograph that makes the customer immediately understand
and desire the proposed renovation.

INPUTS

INPUT IMAGE 1:
A real photograph taken at the customer's property.
Use it as the reference for the identity and architecture
of the real space.

INPUT IMAGE 2:
A technical PrefWeb representation of the window proposed
in the real quotation.
Use it as the primary reference for the geometry,
configuration and appearance of the NEW window.

PRIMARY OBJECTIVE

Show a convincing AFTER version of the customer's real
property after the proposed window has been professionally
installed.

The result should feel noticeably better than the original
customer photograph.

It should look suitable for a premium renovation company's
commercial presentation.

PRESERVE THE PROPERTY

The result must remain recognizably the same real property.

Preserve:
- the architectural identity of the space;
- the location of the window opening;
- the important surrounding architectural elements;
- recognizable structural features;
- enough contextual elements that the customer recognizes
  their own home.

However, you ARE ALLOWED and ENCOURAGED to improve the
photographic presentation.

You may:
- improve exposure and dynamic range;
- correct poor or artificial color casts;
- improve white balance;
- create attractive, realistic natural lighting;
- brighten an excessively dark photograph;
- improve contrast and tonal balance;
- improve sharpness and photographic clarity;
- use a cleaner and more professional composition;
- moderately reframe or crop the scene;
- make a moderate perspective correction;
- choose a slightly improved camera viewpoint when this
  produces a substantially better architectural photograph;
- reduce distracting visual clutter when it does not alter
  the identity of the property;
- make the room feel cleaner, brighter and more inviting.

Do not interpret preservation as a requirement to preserve
poor lighting, poor framing, camera imperfections or an
unattractive photographic appearance.

The AFTER image should be a visual upgrade.

THE NEW WINDOW IS THE MAIN PHYSICAL TRANSFORMATION

The existing window or closure visible in INPUT IMAGE 1
must be replaced by the proposed window represented by
INPUT IMAGE 2.

Do not merely enhance the original photograph while
leaving the existing window unchanged.

The new installed window should be clearly perceptible as
the principal renovation shown in the image.

Use the PrefWeb reference to reproduce the proposed
configuration as faithfully as possible while integrating
it naturally into the real architectural opening.

WINDOW INFORMATION

Room/context:
{window.room or "Not specified"}

PrefWeb description:
{window.description or "Not specified"}

PrefWeb reference:
{window.reference or "Not specified"}

Nomenclature:
{window.nomenclature or "Not specified"}

Color:
{window.color or "Not specified"}

Dimensions:
{window.dimensions or "Not specified"}

The final installation must look physically plausible,
properly fitted and professionally finished.

CUSTOMER NEED

Problem category:
{window.problem_type or "Not specified"}

Commercial notes:
{window.commercial_notes or "None"}

Desired emotional and visual effect:
{problem}

COMMERCIAL VISUAL DIRECTION

This is not a technical documentation image.

It is a premium commercial visualization intended to help
a homeowner imagine how their home could feel after the
renovation.

Aim for the visual quality of professional architectural
and interior photography:
- natural;
- bright but realistic;
- elegant;
- comfortable;
- welcoming;
- clean;
- premium;
- believable.

The benefit should primarily be communicated through the
quality of the renovated space, the new window, lighting,
atmosphere and photographic composition.

HUMAN STORYTELLING

When the customer's problem is easier to understand through
a normal human activity, you are encouraged to include ONE
secondary person in the renovated space.

The person should help the customer intuitively understand
the benefit of the renovation.

Examples of the intended reasoning:

- acoustic/noise problem:
  quietly studying, reading, working or resting;

- thermal comfort problem:
  comfortably enjoying the room in normal indoor clothing
  and a pleasant environment;

- drafts/air infiltration:
  comfortably spending time close to the renovated window
  without visible discomfort;

- security:
  normally communicate the benefit through the quality and
  solidity of the closure rather than staging a person;

- aesthetics:
  normally let the renovated architecture remain the main
  subject.

These are visual intentions, not mandatory literal scenes.
Choose an activity that actually fits the real room shown
in the customer photograph.

The person must:
- appear natural and candid rather than posed;
- remain visually secondary;
- not hide the proposed window;
- not dominate the composition;
- fit the apparent use of the real room;
- improve rather than clutter the photograph.

Do not invent children or imply specific family members.
Do not add multiple people unless they already exist in the
source scene and preserving them is natural.

Do not use exaggerated gestures such as covering ears,
shivering dramatically, sweating, looking frightened or
performing an obvious advertising pose.

The desired effect is subtle:
the viewer should understand the benefit from an ordinary,
comfortable use of the improved space.

DO NOT

- create a completely different room or property;
- move the architectural opening to another wall;
- invent major structural modifications unrelated to the
  window renovation;
- substantially change the size of the opening unless
  required by the quoted solution;
- invent luxury furniture or redesign the entire interior;
- create an obviously staged advertising scene;
- use exaggerated sunlight, glow or cinematic effects;
- create an artificial CGI/render appearance;
- add text, labels, arrows, logos or diagrams;
- preserve the old window unchanged when INPUT IMAGE 2
  clearly represents a different proposed solution.

FINAL PRIORITIES

Prioritize, in this order:

1. Make the proposed PrefWeb window visibly and correctly
   installed.
2. Keep the customer's property recognizably the same.
3. Produce a substantially better and more appealing
   photograph than the source image.
4. Maintain architectural and physical realism.
5. Communicate the customer's expected benefit naturally.
6. Create an image strong enough to be used as the main
   AFTER image in a professional sales presentation.

The final result should make the customer think:
"This is still my home, but this is how much better it
could look and feel after the renovation."
""".strip()
