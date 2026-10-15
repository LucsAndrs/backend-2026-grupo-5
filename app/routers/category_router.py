from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.category_schema import CategoryCreate, CategoryPatch, CategoryResponse
from ..domain.category import Category
from ..schemas.common import PaginatedResponse
from ..services.category_service import category_service

router = APIRouter(prefix="/categorias")


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate) -> Category:
    return category_service.create(data)


@router.get("/", response_model=PaginatedResponse[CategoryResponse])
def get_categories(active: bool | None = None,
                   name: str | None = None,
                   order_by: str = Query("name"),
                   direction: Literal["asc", "desc"] = "asc",
                   page: int = Query(1, ge=1),
                   limit: int = Query(20, ge=1, le=100)) -> PaginatedResponse[CategoryResponse]:
    return category_service.get_categories(active=active, name=name, order_by=order_by,
                                           direction=direction, page=page, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_by_id(category_id: str) -> CategoryResponse:
    return category_service.get_by_id(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: str, data: CategoryPatch) -> CategoryResponse:
    return category_service.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str) -> None:
    category_service.delete(category_id)
