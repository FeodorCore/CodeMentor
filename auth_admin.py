from fastapi import HTTPException, Request
from config import ADMIN_USERNAME, ADMIN_PASSWORD

async def require_admin(request: Request):
    session = request.session
    if not session or session.get("username") != ADMIN_USERNAME:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return session

def verify_admin_password(username: str, password: str) -> bool:
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD