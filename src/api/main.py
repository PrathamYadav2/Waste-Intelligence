import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ..config import get_settings
from .errors import ApiError, api_error_handler
from .logging_setup import setup_logging, new_request_id
from .routes import router, health_router

def create_app() -> FastAPI:
    s = get_settings(); setup_logging(s.log_level)
    app = FastAPI(title="AI Waste Recovery Decision Intelligence", version="0.1.0-scaffold")
    app.add_exception_handler(ApiError, api_error_handler)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(422, {"error": {"code": "VALIDATION_ERROR", "message": "Invalid request.", "details": exc.errors(), "request_id": getattr(request.state, "request_id", None)}})

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = request.headers.get("X-Request-ID") or new_request_id()
        t0 = time.perf_counter(); resp = await call_next(request)
        resp.headers["X-Request-ID"] = request.state.request_id
        resp.headers["X-Response-Time-ms"] = str(int((time.perf_counter() - t0) * 1000))
        return resp

    app.include_router(health_router)
    app.include_router(router, prefix=s.api_prefix)
    ui = Path(__file__).resolve().parents[2] / "app"
    if ui.exists(): app.mount("/", StaticFiles(directory=ui, html=True), name="ui")
    return app

app = create_app()
