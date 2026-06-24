from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from auth_ingress.config import Settings
from auth_ingress.security.csrf import csrf_token
from auth_ingress.services.user_management_types import ManagementFormState

WEB_ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=WEB_ROOT / "templates")


def template(request: Request, name: str, settings: Settings, *, status_code: int = 200, **context):
    if context.get("form_state") is None:
        context["form_state"] = ManagementFormState("none")
    context.setdefault("field_errors", {})
    context.setdefault("form_errors", [])
    response = templates.TemplateResponse(
        request=request,
        name=name,
        context={"csrf_token": csrf_token(settings), **context},
        status_code=status_code,
    )
    response.headers["Cache-Control"] = "no-store"
    return response
