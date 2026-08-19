from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from backend.auth.firebase import (
    AuthenticatedUser,
    require_user,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

CurrentUser = Annotated[
    AuthenticatedUser,
    Depends(require_user),
]


@router.get("/me")
def get_current_user(
    user: CurrentUser,
) -> dict[str, str]:
    return {
        "uid": user.uid,
        "email": user.email,
    }
