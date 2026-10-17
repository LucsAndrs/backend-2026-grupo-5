from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.product_schema import ProductCreate, ProductPatch, ProductResponse
from ..domain.product import Product
from ..schemas.common import PaginatedResponse
from ..services.product_service import product_service

router = APIRouter(prefix="/productos")


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate) -> Product:
    return product_service.create(data)


@router.get("/", response_model=PaginatedResponse[ProductResponse])
def get_products(category_id: str | None = None,
                 name: str | None = None,
                 order_by: str = Query("name"),
                 direction: Literal["asc", "desc"] = "asc",
                 page: int = Query(1, ge=1),
                 limit: int = Query(20, ge=1, le=100)) -> PaginatedResponse[ProductResponse]:
    return product_service.get_products(category_id=category_id, name=name, order_by=order_by,
                                        direction=direction, page=page, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: str) -> ProductResponse:
    return product_service.get_by_id(product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, data: ProductPatch) -> ProductResponse:
    return product_service.update(product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str) -> None:
    product_service.delete(product_id)
