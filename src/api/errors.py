from fastapi import Request
from fastapi.responses import JSONResponse

class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, details=None):
        self.status, self.code, self.message, self.details = status, code, message, details

def not_implemented(feature: str) -> ApiError:
    return ApiError(501, "NOT_IMPLEMENTED_YET", f"{feature} is not implemented yet.")

async def api_error_handler(request: Request, exc: ApiError):
    rid = getattr(request.state, "request_id", None)
    return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message, "details": exc.details, "request_id": rid}})
