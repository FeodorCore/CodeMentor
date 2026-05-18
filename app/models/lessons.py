from pydantic import BaseModel
class LessonCreate(BaseModel):
    category_id: int
    sort_order: int = 0
    title: str
    content: str

class LessonResponse(BaseModel):
    id: int
    category_id: int
    sort_order: int
    title: str
    content: str