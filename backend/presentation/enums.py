from enum import Enum


class SlideType(str, Enum):
    COVER = "cover"

    CURRENT_SITUATION = "current_situation"

    CONSEQUENCES = "consequences"

    PROBLEM_CONFIRMATION = "problem_confirmation"

    SOLUTION_TRANSITION = "solution_transition"

    PROPOSAL = "proposal"

    BENEFITS = "benefits"

    BEFORE_AFTER = "before_after"

    WHY_SMARTVITRA = "why_smartvitra"

    INVESTMENT = "investment"

    FINAL_PRICE = "final_price"

    CLOSING = "closing"


class SlideMode(str, Enum):
    FIXED = "fixed"
    SEMI_DYNAMIC = "semi_dynamic"
    DYNAMIC = "dynamic"
