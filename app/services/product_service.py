from datetime import datetime
import math
from ..excepciones import BusinessRuleError
from ..domain.product import Product
from ..schemas.product_schema import ProductCreate, ProductPatch, ProductResponse
from ..schemas.common import PaginatedResponse
from ..repositories.category_repository import category_repository
from ..repositories.product_repository import product_repository

ORDER_FIELDS = {"name", "description", "stock", "min_stock",
                "category_id", "price", "created_at", "updated_at"}


class ProductService:
    def _to_response(self, product: Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            stock=product.stock,
            min_stock=product.min_stock,
            category_id=product.category_id,
            price=product.price,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def create(self, data: ProductCreate) -> Product:
        category_repository.get_by_id(data.category_id)
        entity = Product(**data.model_dump())
        return product_repository.create(entity)

    def get_products(self,
                     category_id: str | None = None,
                     name: str | None = None,
                     order_by: str = "name",
                     direction: str = "asc",
                     page: int = 1,
                     limit: int = 20) -> PaginatedResponse[ProductResponse]:
        if order_by not in ORDER_FIELDS:
            raise BusinessRuleError(f"El campo '{order_by}' no es válido para ordenar")

        filtered = product_repository.get_all()
        if category_id is not None:
            filtered = [p for p in filtered if p.category_id == category_id]
        if name:
            filtered = [p for p in filtered if name.lower() in p.name.lower()]

        reverse = direction == "desc"
        filtered = sorted(filtered, key=lambda p: getattr(p, order_by), reverse=reverse)

        total = len(filtered)
        total_pages = math.ceil(total / limit) if total > 0 else 0
        start = (page - 1) * limit
        items = [self._to_response(p) for p in filtered[start:start + limit]]

        return PaginatedResponse(items=items, total=total, pagina=page,
                                 limite=limit, total_paginas=total_pages)

    def get_by_id(self, product_id: str) -> ProductResponse:
        return self._to_response(product_repository.get_by_id(product_id))

    def update(self, product_id: str, data: ProductPatch) -> ProductResponse:
        entity = product_repository.get_by_id(product_id)
        if data.name is not None:
            entity.name = data.name
        if data.description is not None:
            entity.description = data.description
        if data.stock is not None:
            entity.stock = data.stock
        if data.min_stock is not None:
            entity.min_stock = data.min_stock
        if data.category_id is not None:
            category_repository.get_by_id(data.category_id)
            entity.category_id = data.category_id
        if data.price is not None:
            entity.price = data.price
        entity.updated_at = datetime.now()
        return self._to_response(product_repository.update(product_id, entity))

    def delete(self, product_id: str) -> None:
        return product_repository.delete(product_id)


product_service = ProductService()
