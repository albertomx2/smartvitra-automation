from pathlib import Path

from backend.catalog.loader import (
    build_default_catalog,
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
from backend.services.proposal_normalizer import (
    ProposalNormalizer,
)

catalog = build_default_catalog()

pdf_path = Path("assets/examples/Pedido - S00122.pdf")

visit_path = Path("tests/fixtures/visits/" "example_noise_thermal.json")

reader = PdfTextReader()
parser = PdfProposalParser()
normalizer = ProposalNormalizer()

raw = parser.parse(reader.read(pdf_path))

proposal = normalizer.normalize(raw)

enrichment = ProposalEnrichmentInput.model_validate_json(
    visit_path.read_text(encoding="utf-8")
)

enrichment_service = ProposalEnrichmentService(
    product_enricher=ProductEnricher(catalog),
    customer_needs_service=(CustomerNeedsService()),
)

enriched = enrichment_service.enrich(
    proposal,
    enrichment,
)

matcher = BenefitMatcher(catalog)

result = matcher.match(enriched)

print(result.model_dump_json(indent=2))
