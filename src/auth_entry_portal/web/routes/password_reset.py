from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth_entry_portal.config import Settings, get_settings
from auth_entry_portal.repositories.database import get_db
from auth_entry_portal.security.csrf import valid_csrf
from auth_entry_portal.services.password_reset_service import complete_reset, encode_reset_cookie, validate_reset_token
from auth_entry_portal.services.user_management_types import ManagementError
from auth_entry_portal.web.web import template

router = APIRouter()


@router.get("/reset-password")
def reset_form(request: Request, token: str | None = None, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if token:
        try:
            validate_reset_token(db, token)
        except ManagementError:
            return template(request, "auth/reset_password.html", settings, error="Reset request is invalid or expired", status_code=400)
        response = RedirectResponse("/reset-password", status_code=303)
        response.set_cookie(settings.reset_cookie, encode_reset_cookie(token, settings), httponly=True, secure=settings.secure_cookies, samesite="strict", max_age=settings.password_reset_ttl_seconds, path="/reset-password")
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
    response = template(request, "auth/reset_password.html", settings, error=None)
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@router.post("/reset-password")
def reset_complete(request: Request, password: str = Form(...), password_confirm: str = Form(...), csrf: str = Form(...), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    if not valid_csrf(csrf, settings) or password != password_confirm:
        response = template(request, "auth/reset_password.html", settings, error="The request expired or passwords did not match", status_code=400)
    else:
        try:
            complete_reset(db, request.cookies.get(settings.reset_cookie), password, settings)
        except (ManagementError, ValueError):
            response = template(request, "auth/reset_password.html", settings, error="Reset request is invalid or expired", status_code=400)
        else:
            response = RedirectResponse("/sign-in?reset=1", status_code=303)
    response.delete_cookie(settings.reset_cookie, path="/reset-password")
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
