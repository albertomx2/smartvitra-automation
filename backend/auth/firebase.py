from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

import firebase_admin  # type: ignore[import-untyped]
from fastapi import (
    Header,
    HTTPException,
    status,
)
from firebase_admin import auth


@dataclass(frozen=True)
class AuthenticatedUser:
    uid: str
    email: str


def _allowed_emails() -> set[str]:
    raw = os.getenv(
        "SMARTVITRA_ALLOWED_EMAILS",
        "",
    )

    return {value.strip().lower() for value in raw.split(",") if value.strip()}


@lru_cache(maxsize=1)
def _initialize_firebase() -> None:
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app()


def require_user(
    authorization: str | None = Header(
        default=None,
    ),
) -> AuthenticatedUser:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    scheme, _, token = authorization.partition(
        " ",
    )

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    _initialize_firebase()

    try:
        decoded = auth.verify_id_token(
            token,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    email = decoded.get("email")
    email_verified = decoded.get(
        "email_verified",
        False,
    )
    uid = decoded.get("uid")

    if not isinstance(email, str) or not isinstance(uid, str) or not email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified Google account required",
        )

    normalized_email = email.lower()

    if normalized_email not in _allowed_emails():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized for SmartVitra",
        )

    return AuthenticatedUser(
        uid=uid,
        email=normalized_email,
    )
