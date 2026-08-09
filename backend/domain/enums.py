from enum import Enum


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    NORMALIZING = "normalizing"

    GENERATING_PRESENTATION = "generating_presentation"
    VALIDATING_PRESENTATION = "validating_presentation"

    GENERATING_SCRIPT = "generating_script"
    GENERATING_VIDEO = "generating_video"

    READY_FOR_REVIEW = "ready_for_review"

    APPROVED = "approved"
    SENT = "sent"

    FAILED = "failed"


class SourceType(str, Enum):
    PDF = "pdf"
    PREFWEB = "prefweb"
    ODOO = "odoo"
    MANUAL = "manual"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    CONFLICT = "conflict"


class PhotoType(str, Enum):
    OVERVIEW = "overview"
    DETAIL = "detail"
    PROBLEM = "problem"
    FACADE = "facade"
    OTHER = "other"


class GeneratedAssetType(str, Enum):
    PRESENTATION = "presentation"
    PRESENTATION_PDF = "presentation_pdf"
    SCRIPT = "script"
    AUDIO = "audio"
    VIDEO = "video"
    AI_VISUALIZATION = "ai_visualization"


class ValidationSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
