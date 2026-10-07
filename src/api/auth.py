"""Authentication placeholder (AUTH_MODE=placeholder lets every request through). NOT_IMPLEMENTED_YET."""
from fastapi import Request
async def require_user(request: Request):
    return None
