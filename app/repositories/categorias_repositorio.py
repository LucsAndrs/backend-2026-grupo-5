from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.categorias import Categoria
from ..excepciones import ConflictError, ResourceNotFoundError
from ..models.categoria_modelos import CategoriaBD
from ..models.producto_modelos import ProductoBD


class CategoriaRepositorio:
    def crear(self, bd: Session, entidad: Categoria) -> Categoria:
        existe = bd.query(CategoriaBD).filter(
            func.lower(CategoriaBD.nombre_categoria) == entidad.nombre_categoria.lower()
        ).first()
        if existe:
            raise ConflictError(f"Ya existe una categoría con el nombre '{entidad.nombre_categoria}'")
        bd.add(self._a_bd(entidad))
        bd.commit()
        return entidad

    def obtener_todas(self, bd: Session) -> list[Categoria]:
        return [self._a_entidad(c) for c in bd.query(CategoriaBD).all()]

    def obtener_por_id(self, bd: Session, id_categoria: str) -> Categoria:
        categoria = bd.query(CategoriaBD).filter(CategoriaBD.id_categoria == id_categoria).first()
        if categoria is None:
            raise ResourceNotFoundError("No existe una categoría con el ID solicitado")
        return self._a_entidad(categoria)

    def actualizar(self, bd: Session, id_categoria: str, entidad: Categoria) -> Categoria:
        categoria = bd.query(CategoriaBD).filter(CategoriaBD.id_categoria == id_categoria).first()
        if categoria is None:
            raise ResourceNotFoundError("No existe una categoría con el ID solicitado")
        categoria.nombre_categoria = entidad.nombre_categoria
        categoria.descripcion = entidad.descripcion
        categoria.activa = entidad.activa
        categoria.fecha_actualizacion = entidad.fecha_actualizacion
        bd.commit()
        return entidad

    def eliminar(self, bd: Session, id_categoria: str) -> None:
        categoria = bd.query(CategoriaBD).filter(CategoriaBD.id_categoria == id_categoria).first()
        if categoria is None:
            raise ResourceNotFoundError("No existe una categoría con el ID solicitado")

        productos_asociados = bd.query(ProductoBD.id_producto).filter(
            ProductoBD.id_categoria == id_categoria
        ).first()
        if productos_asociados is not None:
            raise ConflictError(
                "No se puede eliminar la categoría porque tiene productos asociados"
            )

        try:
            bd.delete(categoria)
            bd.commit()
        except IntegrityError:
            bd.rollback()
            raise ConflictError(
                "No se puede eliminar la categoría porque tiene relaciones asociadas"
            )

    def _a_bd(self, entidad: Categoria) -> CategoriaBD:
        return CategoriaBD(
            id_categoria=entidad.id_categoria,
            nombre_categoria=entidad.nombre_categoria,
            descripcion=entidad.descripcion,
            activa=entidad.activa,
            fecha_creacion=entidad.fecha_creacion,
            fecha_actualizacion=entidad.fecha_actualizacion,
        )

    def _a_entidad(self, categoria: CategoriaBD) -> Categoria:
        return Categoria(
            id_categoria=categoria.id_categoria,
            nombre_categoria=categoria.nombre_categoria,
            descripcion=categoria.descripcion,
            activa=categoria.activa,
            fecha_creacion=categoria.fecha_creacion,
            fecha_actualizacion=categoria.fecha_actualizacion,
        )


categoria_repositorio = CategoriaRepositorio()
