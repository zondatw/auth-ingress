from __future__ import annotations

import hashlib

from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse


def create_downstream_app() -> FastAPI:
    app = FastAPI()

    page = """<!doctype html><html><head>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="stylesheet" href="static/relative.css">
    <link rel="preload" href="/static/font.woff2" as="font" crossorigin>
    <script src="/static/app.js" defer></script></head>
    <body><h1>Fixture App</h1><img id="logo" src="/static/logo.svg" alt="Fixture logo">
    <a id="nested" href="/nested/page">Nested page</a><output id="api-result"></output>
    <form action="/form" method="post"><input name="value" value="saved"><button>Submit</button></form>
    </body></html>"""

    @app.get("/")
    async def home():
        return HTMLResponse(page)

    @app.get("/nested/page")
    async def nested():
        return HTMLResponse('<h1>Nested Page</h1><a href="/">Home</a>')

    @app.api_route("/static/style.css", methods=["GET", "HEAD"])
    async def style():
        return Response("body{background:rgb(245,247,251)}", media_type="text/css")

    @app.get("/static/relative.css")
    async def relative_style():
        return Response("h1{color:rgb(23,33,58)}", media_type="text/css")

    @app.get("/static/app.js")
    async def script():
        return Response("fetch('/api/data?item=a&item=b').then(r=>r.json()).then(v=>document.querySelector('#api-result').textContent=v.items.join(','));", media_type="application/javascript")

    @app.get("/static/logo.svg")
    async def image():
        return Response('<svg xmlns="http://www.w3.org/2000/svg"><circle cx="8" cy="8" r="8"/></svg>', media_type="image/svg+xml")

    @app.get("/static/font.woff2")
    async def font():
        return Response(b"fixture-font", media_type="font/woff2")

    @app.get("/document.txt")
    async def document():
        return Response("fixture document", media_type="text/plain")

    @app.api_route("/api/data", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def api_data(request: Request):
        body = await request.body()
        return JSONResponse({"method": request.method, "items": request.query_params.getlist("item"), "body": body.decode(errors="replace")})

    @app.post("/form")
    async def form(request: Request):
        data = await request.form()
        return HTMLResponse(f"<h1>Form Result</h1><p>{data.get('value')}</p>")

    @app.post("/upload")
    async def upload(request: Request):
        digest = hashlib.sha256()
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            digest.update(chunk)
        return JSONResponse({"size": size, "sha256": digest.hexdigest()})

    @app.get("/download")
    async def download(size: int = 1024):
        async def chunks():
            remaining = min(size, 100 * 1024 * 1024)
            block = b"proxy-download-" * 4096
            while remaining:
                chunk = block[: min(remaining, len(block))]
                remaining -= len(chunk)
                yield chunk

        return StreamingResponse(chunks(), media_type="application/octet-stream", headers={"Content-Disposition": 'attachment; filename="fixture.bin"', "ETag": '"fixture"'})

    @app.get("/range")
    async def range_response(request: Request):
        content = b"0123456789"
        if request.headers.get("range") == "bytes=2-5":
            return Response(content[2:6], status_code=206, headers={"Content-Range": "bytes 2-5/10", "Accept-Ranges": "bytes"})
        return Response(content, headers={"Accept-Ranges": "bytes"})

    @app.get("/cookie")
    async def cookie(request: Request):
        response = JSONResponse({"state": request.cookies.get("app_state")})
        response.set_cookie("app_state", "fixture", httponly=True, path="/")
        response.headers.append("set-cookie", "auth_portal_service=forged; Path=/; HttpOnly")
        return response

    @app.get("/redirect/internal")
    async def internal_redirect():
        return RedirectResponse("/nested/page", status_code=302)

    @app.get("/redirect/absolute")
    async def absolute_redirect(request: Request):
        return RedirectResponse(str(request.base_url).rstrip("/") + "/nested/page", status_code=302)

    @app.get("/redirect/external")
    async def external_redirect():
        return RedirectResponse("https://public.example/escape", status_code=302)

    @app.websocket("/ws")
    async def websocket_echo(websocket: WebSocket):
        offered = websocket.scope.get("subprotocols", [])
        await websocket.accept(subprotocol="fixture" if "fixture" in offered else None)
        try:
            while True:
                message = await websocket.receive()
                if message.get("text") is not None:
                    await websocket.send_text(message["text"])
                elif message.get("bytes") is not None:
                    await websocket.send_bytes(message["bytes"])
                else:
                    break
        except Exception:
            pass

    return app
