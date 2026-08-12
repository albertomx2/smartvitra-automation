from decimal import Decimal

from backend.catalog.loader import (
    build_default_catalog,
)
from backend.commercial.builder import (
    CommercialBriefBuilder,
)
from backend.domain.enums import (
    PhotoType,
)
from backend.domain.proposal import (
    Customer,
    CustomerNeed,
    GlassConfiguration,
    Opening,
    PaymentTerms,
    Photo,
    Pricing,
    ProductReference,
    Proposal,
)
from backend.matching.benefit_matcher import (
    BenefitMatcher,
)
from backend.presentation.builder import (
    PresentationSpecBuilder,
)


def build_manolo_spec():
    catalog = build_default_catalog()

    proposal = Proposal(
        proposal_number="FAKE-MANOLO-001",
        customer=Customer(
            name="Manolo García",
            city="Sevilla",
        ),
        openings=[
            Opening(
                id="V1",
                room="Salón",
                window_type="Ventana 2 hojas",
                glass=GlassConfiguration(
                    description=("Vidrio con Control Solar + argón"),
                    control_solar=True,
                    low_emissivity=False,
                    argon=True,
                ),
            ),
            Opening(
                id="V2",
                room="Dormitorio",
                window_type="Ventana 2 hojas",
                glass=GlassConfiguration(
                    description=("Vidrio con Control Solar + argón"),
                    control_solar=True,
                    low_emissivity=False,
                    argon=True,
                ),
            ),
            Opening(
                id="V3",
                room="Dormitorio",
                window_type="Ventana 1 hoja",
                glass=GlassConfiguration(
                    description=("Vidrio con Bajo Emisivo + argón"),
                    control_solar=False,
                    low_emissivity=True,
                    argon=True,
                ),
            ),
        ],
        products=[
            ProductReference(
                product_code="UNIK",
                name="UNIK",
                relevant_to_openings=[
                    "V1",
                    "V2",
                    "V3",
                ],
            ),
            ProductReference(
                product_code="THERMOACUSTIC",
                name="Cajón SUMUM Thermoacustic",
                relevant_to_openings=[
                    "V1",
                    "V2",
                ],
            ),
        ],
        customer_needs=[
            CustomerNeed(
                code="summer_heat",
                description=("La vivienda acumula mucho calor " "durante el verano."),
                priority=5,
                source_text=(
                    "En invierno estoy bien, pero en verano "
                    "hace muchísimo calor en casa, sobre todo "
                    "por la tarde."
                ),
            ),
            CustomerNeed(
                code="acoustic_noise",
                description=(
                    "El cliente da mucha importancia "
                    "al aislamiento frente al ruido exterior."
                ),
                priority=5,
                source_text=(
                    "El ruido del tráfico me molesta bastante, "
                    "especialmente cuando intento descansar."
                ),
            ),
            CustomerNeed(
                code="light",
                description=(
                    "El cliente quiere conservar o mejorar "
                    "la entrada de luz natural."
                ),
                priority=4,
                source_text=(
                    "Ahora entra poca luz y no quiero que "
                    "las ventanas nuevas hagan la casa "
                    "todavía más oscura."
                ),
            ),
            CustomerNeed(
                code="aesthetics",
                description=(
                    "El cliente valora que la solución "
                    "mejore visualmente la vivienda."
                ),
                priority=2,
                source_text=("Si además se ve más moderno, mejor."),
            ),
        ],
        photos=[
            Photo(
                opening_id="V1",
                photo_type=PhotoType.PROBLEM,
                storage_key=("visits/FAKE-MANOLO-001/" "photos/V1/problem_01.jpg"),
                usage=[
                    "current_problem",
                    "problem_confirmation",
                    "before_after",
                ],
                description=("Ventana del salón expuesta al sol."),
            ),
        ],
        pricing=Pricing(
            currency="EUR",
            usual_cost=Decimal("5200.00"),
            subtotal=Decimal("3454.55"),
            tax_total=Decimal("725.45"),
            total=Decimal("4180.00"),
            payment_terms=PaymentTerms(
                description=(
                    "50 % al aprobar el presupuesto. "
                    "30 % antes de la instalación. "
                    "20 % al finalizar."
                )
            ),
        ),
    )

    matches = BenefitMatcher(catalog).match(proposal)

    brief = CommercialBriefBuilder(catalog).build(
        proposal,
        matches,
    )

    return PresentationSpecBuilder().build(brief)


spec = build_manolo_spec()
