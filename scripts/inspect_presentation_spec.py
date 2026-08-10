from pathlib import Path

from backend.catalog.loader import (
    build_default_catalog,
)
from backend.commercial.builder import (
    CommercialBriefBuilder,
)
from backend.enrichment.models import (
    ProposalEnrichmentInput,
)
from backend.enrichment.product_enricher import (
    ProductEnricher,
)
from backend.enrichment.service import (
    ProposalEnrichmentService,
)
from backend.integrations.pdf.parser import (
    PdfProposalParser,
)
from backend.integrations.pdf.reader import (
    PdfTextReader,
)
from backend.matching.benefit_matcher import (
    BenefitMatcher,
)
from backend.needs.service import (
    CustomerNeedsService,
)
from backend.presentation.builder import (
    PresentationSpecBuilder,
)
from backend.services.proposal_normalizer import (
    ProposalNormalizer,
)

catalog = build_default_catalog()

pdf_path = Path("assets/examples/Pedido - S00122.pdf")

visit_path = Path("tests/fixtures/visits/" "example_noise_thermal.json")

proposal = ProposalNormalizer().normalize(
    PdfProposalParser().parse(PdfTextReader().read(pdf_path))
)

enrichment = ProposalEnrichmentInput.model_validate_json(
    visit_path.read_text(encoding="utf-8")
)

proposal = ProposalEnrichmentService(
    product_enricher=ProductEnricher(catalog),
    customer_needs_service=(CustomerNeedsService()),
).enrich(
    proposal,
    enrichment,
)

matches = BenefitMatcher(catalog).match(proposal)

brief = CommercialBriefBuilder(catalog).build(
    proposal,
    matches,
)

spec = PresentationSpecBuilder().build(brief)

print(spec.model_dump_json(indent=2))
