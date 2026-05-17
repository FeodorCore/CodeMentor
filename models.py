from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ----- Category -----
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# ----- Article -----
class ArticleBase(BaseModel):
    category_id: int
    title: str
    content: Optional[str] = None
    schedule_at: Optional[datetime] = None
    status: str = "draft"

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ----- Question -----
class QuestionBase(BaseModel):
    article_id: int
    text: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    class Config:
        from_attributes = True

# ----- Answer -----
class AnswerBase(BaseModel):
    question_id: int
    text: str
    is_correct: bool = False

class AnswerCreate(AnswerBase):
    pass

class Answer(AnswerBase):
    id: int
    class Config:
        from_attributes = True

# ----- Users -----
class UserBase(BaseModel):
    tg_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# ----- UserHistory -----
class UserHistoryBase(BaseModel):
    user_id: int
    question_id: int
    answer_id: int
    is_right: bool

class UserHistoryCreate(UserHistoryBase):
    pass

class UserHistory(UserHistoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ----- MailingLog -----
class MailingLogBase(BaseModel):
    article_id: int
    user_id: int

class MailingLogCreate(MailingLogBase):
    pass

class MailingLog(MailingLogBase):
    id: int
    sent_at: datetime
    class Config:
        from_attributes = True