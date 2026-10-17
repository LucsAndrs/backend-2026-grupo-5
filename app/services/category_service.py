from datetime import datetime
import math
from ..excepciones import BusinessRuleError
from ..domain.category import Category
from ..schemas.category_schema import CategoryCreate, CategoryPatch, CategoryResponse
from ..schemas.common import PaginatedResponse
from ..repositories.category_repository import category_repository
from ..repositories.product_repository import product_repository

ORDER_FIELDS = {"name", "description", "active", "created_at", "updated_at"}


class CategoryService:
    def _to_response(self, category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            active=category.active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            product_count=product_repository.count_by_category(category.id),
        )

    def create(self, data: CategoryCreate) -> Category:
        entity = Category(**data.model_dump())
        return category_repository.create(entity)

    def get_categories(self, active: bool | None = None,
                       name: str | None = None,
                       order_by: str = "name",
                       direction: str = "asc",
                       page: int = 1,
                       limit: int = 20) -> PaginatedResponse[CategoryResponse]:
        if order_by not in ORDER_FIELDS:
            raise BusinessRuleError(f"El campo '{order_by}' no es válido para ordenar")

        filtered = category_repository.get_all()
        if active is not None:
            filtered = [c for c in filtered if c.active == active]
        if name:
            filtered = [c for c in filtered if name.lower() in c.name.lower()]

        reverse = direction == "desc"
        filtered = sorted(filtered, key=lambda c: getattr(c, order_by), reverse=reverse)

        total = len(filtered)
        total_pages = math.ceil(total / limit) if total > 0 else 0
        start = (page - 1) * limit
        items = [self._to_response(c) for c in filtered[start:start + limit]]

        return PaginatedResponse(items=items, total=total, pagina=page,
                                 limite=limit, total_paginas=total_pages)

    def get_by_id(self, category_id: str) -> CategoryResponse:
        return self._to_response(category_repository.get_by_id(category_id))

    def update(self, category_id: str, data: CategoryPatch) -> CategoryResponse:
        entity = category_repository.get_by_id(category_id)
        if data.name is not None:
            entity.name = data.name
        if data.description is not None:
            entity.description = data.description
        if data.active is not None:
            entity.active = data.active
        entity.updated_at = datetime.now()
        category_repository.update(category_id, entity)
        return self._to_response(entity)

    def delete(self, category_id: str) -> None:
        return category_repository.delete(category_id)


category_service = CategoryService()
