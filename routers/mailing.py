from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_api_key

router = APIRouter(prefix="/mailing", tags=["mailing"])

class MailingRequest(BaseModel):
    article_id: int

@router.post("/send", dependencies=[Depends(verify_api_key)])
def send_mailing(req: MailingRequest):
    # Пока заглушка — будет реализовано в части 5
    return {"message": f"Рассылка статьи {req.article_id} будет запущена", "status": "pending"}