from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from auth_entry_portal.config import Settings
from auth_entry_portal.security.csrf import csrf_token

WEB_ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=WEB_ROOT / "templates")


def template(request: Request, name: str, settings: Settings, *, status_code: int = 200, **context):
    response = templates.TemplateResponse(
        request=request,
        name=name,
        context={"csrf_token": csrf_token(settings), **context},
        status_code=status_code,
    )
    response.headers["Cache-Control"] = "no-store"
    return response

