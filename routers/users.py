from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from crud import register_user, get_user_by_tg_id, get_user_history_for_article
from auth import verify_api_key

router = APIRouter(prefix="/users", tags=["users"])


class UserRegister(BaseModel):
    tg_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None


@router.post("/register", dependencies=[Depends(verify_api_key)])
def register(user: UserRegister) -> Dict[str, Any]:
    user_id = register_user(user.tg_id, user.username, user.full_name)
    return {"user_id": user_id, "message": "ok"}


@router.get("/{tg_id}/history", dependencies=[Depends(verify_api_key)])
def get_user_history(tg_id: int, article_id: Optional[int] = None) -> List[Dict[str, Any]]:
    user = get_user_by_tg_id(tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if article_id:
        history = get_user_history_for_article(user["id"], article_id)
    else:
        # можно сделать получение всей истории, но пока только по статье
        history = []  # заглушка
    return history