from ..excepciones import ConflictError, ResourceNotFoundError
from ..domain.category import Category


class CategoryRepository:
    def __init__(self):
        self._categories: list[Category] = []

    def create(self, entity: Category) -> Category:
        if any(cat.name.lower() == entity.name.lower() for cat in self._categories):
            raise ConflictError(f"Ya existe una categoría con el nombre '{entity.name}'")
        self._categories.append(entity)
        return entity

    def get_all(self) -> list[Category]:
        return self._categories

    def get_by_id(self, category_id: str) -> Category:
        for category in self._categories:
            if category.id == category_id:
                return category
        raise ResourceNotFoundError("No existe una categoría con el ID solicitado")

    def update(self, category_id: str, entity: Category) -> Category:
        for idx, category in enumerate(self._categories):
            if category.id == category_id:
                self._categories[idx] = entity
                return self._categories[idx]
        raise ResourceNotFoundError("No existe una categoría con el ID solicitado")

    def delete(self, category_id: str) -> None:
        for idx, category in enumerate(self._categories):
            if category.id == category_id:
                self._categories.pop(idx)
                return None
        raise ResourceNotFoundError("No existe una categoría con el ID solicitado")


category_repository = CategoryRepository()
