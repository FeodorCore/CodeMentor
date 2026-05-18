# admin_routes.py
from fastapi import APIRouter, HTTPException
from services import CategoryService
from models import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

category_service = CategoryService()

@router.get("/categories", response_model=list[CategoryResponse])
def get_categories():
    """Получить список всех категорий."""
    try:
        return category_service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate):
    """Создать новую категорию."""
    try:
        return category_service.create(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int):
    """Удалить категорию по ID."""
    try:
        success = category_service.delete(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))