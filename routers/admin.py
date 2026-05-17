from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from auth_admin import require_admin, verify_admin_password
from crud import (
    get_categories, create_category, update_category, delete_category,
    get_all_articles, get_article, create_article, update_article, delete_article,
    create_question, get_questions_by_article, delete_question,
    create_answer, get_answers_by_question, delete_answer,
)
from typing import Optional
from database import db

router = APIRouter(prefix="/admin", tags=["admin"])

# Настройка Jinja2 без кэширования
templates_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0
)

def render_template(name: str, request: Request, **context):
    template = templates_env.get_template(name)
    content = template.render(request=request, **context)
    return HTMLResponse(content=content)

# ---------- Логин и логаут ----------
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return render_template("login.html", request, error=error)

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_admin_password(username, password):
        request.session["username"] = username
        return RedirectResponse(url="/admin", status_code=303)
    else:
        return RedirectResponse(url="/admin/login?error=Invalid credentials", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login")

# ---------- Главная ----------
@router.get("/", response_class=HTMLResponse)
async def admin_home(request: Request, _=Depends(require_admin)):
    return render_template("index.html", request)

# ---------- Категории ----------
@router.get("/categories", response_class=HTMLResponse)
async def list_categories(request: Request, _=Depends(require_admin)):
    categories = get_categories()
    return render_template("categories.html", request, categories=categories)

@router.post("/categories/create")
async def create_category_route(name: str = Form(...), parent_id: Optional[int] = Form(None), _=Depends(require_admin)):
    create_category(name, parent_id)
    return RedirectResponse(url="/admin/categories", status_code=303)

@router.post("/categories/update/{category_id}")
async def update_category_route(category_id: int, name: str = Form(...), parent_id: Optional[int] = Form(None), _=Depends(require_admin)):
    update_category(category_id, name, parent_id)
    return RedirectResponse(url="/admin/categories", status_code=303)

@router.get("/categories/delete/{category_id}")
async def delete_category_route(category_id: int, _=Depends(require_admin)):
    delete_category(category_id)
    return RedirectResponse(url="/admin/categories", status_code=303)

# ---------- Статьи ----------
@router.get("/articles", response_class=HTMLResponse)
async def list_articles(request: Request, _=Depends(require_admin)):
    articles = get_all_articles()
    categories = get_categories()
    cat_dict = {c["id"]: c["name"] for c in categories}
    return render_template("articles.html", request, articles=articles, categories=cat_dict)

@router.get("/articles/create", response_class=HTMLResponse)
async def create_article_form(request: Request, _=Depends(require_admin)):
    categories = get_categories()
    return render_template("article_form.html", request, categories=categories, article=None)

@router.post("/articles/create")
async def create_article_route(
    category_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(None),
    schedule_at: str = Form(None),
    status: str = Form("draft"),
    _=Depends(require_admin)
):
    create_article(category_id, title, content, schedule_at, status)
    return RedirectResponse(url="/admin/articles", status_code=303)

@router.get("/articles/edit/{article_id}", response_class=HTMLResponse)
async def edit_article_form(request: Request, article_id: int, _=Depends(require_admin)):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404)
    categories = get_categories()
    return render_template("article_form.html", request, categories=categories, article=article)

@router.post("/articles/update/{article_id}")
async def update_article_route(
    article_id: int,
    category_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(None),
    schedule_at: str = Form(None),
    status: str = Form("draft"),
    _=Depends(require_admin)
):
    update_article(article_id, category_id=category_id, title=title, content=content, schedule_at=schedule_at, status=status)
    return RedirectResponse(url="/admin/articles", status_code=303)

@router.get("/articles/delete/{article_id}")
async def delete_article_route(article_id: int, _=Depends(require_admin)):
    delete_article(article_id)
    return RedirectResponse(url="/admin/articles", status_code=303)

# ---------- Управление вопросами и ответами ----------
@router.get("/articles/{article_id}", response_class=HTMLResponse)
async def article_detail(request: Request, article_id: int, _=Depends(require_admin)):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404)
    questions = get_questions_by_article(article_id)
    for q in questions:
        q["answers"] = get_answers_by_question(q["id"])
    return render_template("article_detail.html", request, article=article, questions=questions)

@router.post("/articles/{article_id}/questions/create")
async def create_question_route(article_id: int, text: str = Form(...), _=Depends(require_admin)):
    create_question(article_id, text)
    return RedirectResponse(url=f"/admin/articles/{article_id}", status_code=303)

@router.get("/articles/{article_id}/questions/delete/{question_id}")
async def delete_question_route(article_id: int, question_id: int, _=Depends(require_admin)):
    delete_question(question_id)
    return RedirectResponse(url=f"/admin/articles/{article_id}", status_code=303)

@router.post("/questions/{question_id}/answers/create")
async def create_answer_route(question_id: int, text: str = Form(...), is_correct: bool = Form(False), _=Depends(require_admin)):
    row = db.fetch_one("SELECT article_id FROM Question WHERE id = ?", (question_id,))
    article_id = row["article_id"] if row else 1
    create_answer(question_id, text, is_correct)
    return RedirectResponse(url=f"/admin/articles/{article_id}", status_code=303)

@router.get("/answers/delete/{answer_id}")
async def delete_answer_route(answer_id: int, _=Depends(require_admin)):
    row = db.fetch_one("SELECT question_id FROM Answer WHERE id = ?", (answer_id,))
    if row:
        qid = row["question_id"]
        row2 = db.fetch_one("SELECT article_id FROM Question WHERE id = ?", (qid,))
        article_id = row2["article_id"] if row2 else 1
    else:
        article_id = 1
    delete_answer(answer_id)
    return RedirectResponse(url=f"/admin/articles/{article_id}", status_code=303)

# ---------- Пользователи и история ----------
@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, _=Depends(require_admin)):
    users = db.fetch_all("SELECT id, tg_id, username, full_name, is_active FROM Users")
    users = [dict(u) for u in users]
    return render_template("users.html", request, users=users)

@router.get("/users/{user_id}/history", response_class=HTMLResponse)
async def user_history(request: Request, user_id: int, _=Depends(require_admin)):
    user = db.fetch_one("SELECT * FROM Users WHERE id = ?", (user_id,))
    if not user:
        raise HTTPException(status_code=404)
    history = db.fetch_all("""
        SELECT uh.*, q.text as question_text, a.text as answer_text, ar.title as article_title
        FROM UserHistory uh
        JOIN Question q ON uh.question_id = q.id
        JOIN Answer a ON uh.answer_id = a.id
        JOIN Article ar ON q.article_id = ar.id
        WHERE uh.user_id = ?
        ORDER BY uh.created_at DESC
    """, (user_id,))
    history = [dict(h) for h in history]
    return render_template("user_history.html", request, user=user, history=history)