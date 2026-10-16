from ..excepciones import ConflictError, ResourceNotFoundError
from ..domain.product import Product


class ProductRepository:
    def __init__(self):
        self._products: list[Product] = []

    def create(self, entity: Product) -> Product:
        if any(prod.name.lower() == entity.name.lower() for prod in self._products):
            raise ConflictError(f"Ya existe un producto con el nombre '{entity.name}'")
        self._products.append(entity)
        return entity

    def get_all(self) -> list[Product]:
        return self._products

    def get_by_id(self, product_id: str) -> Product:
        for product in self._products:
            if product.id == product_id:
                return product
        raise ResourceNotFoundError("No existe un producto con el ID solicitado")

    def update(self, product_id: str, entity: Product) -> Product:
        for idx, product in enumerate(self._products):
            if product.id == product_id:
                self._products[idx] = entity
                return self._products[idx]
        raise ResourceNotFoundError("No existe un producto con el ID solicitado")

    def delete(self, product_id: str) -> None:
        for idx, product in enumerate(self._products):
            if product.id == product_id:
                self._products.pop(idx)
                return None
        raise ResourceNotFoundError("No existe un producto con el ID solicitado")

    def count_by_category(self, category_id: str) -> int:
        return sum(1 for product in self._products if product.category_id == category_id)


product_repository = ProductRepository()
