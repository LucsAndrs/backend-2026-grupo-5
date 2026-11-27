from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.productos import Producto
from ..excepciones import ConflictError, ResourceNotFoundError
from ..models.detalle_venta_modelos import DetalleVentaBD
from ..models.producto_modelos import ProductoBD


class ProductoRepositorio:
    def crear(self, bd: Session, entidad: Producto) -> Producto:
        existe = bd.query(ProductoBD).filter(
            func.lower(ProductoBD.nombre_producto) == entidad.nombre_producto.lower()
        ).first()
        if existe:
            raise ConflictError(f"Ya existe un producto con el nombre '{entidad.nombre_producto}'")
        bd.add(self._a_bd(entidad))
        bd.commit()
        return entidad

    def obtener_todos(self, bd: Session) -> list[Producto]:
        return [self._a_entidad(p) for p in bd.query(ProductoBD).all()]

    def obtener_por_id(self, bd: Session, id_producto: str) -> Producto:
        producto = bd.query(ProductoBD).filter(ProductoBD.id_producto == id_producto).first()
        if producto is None:
            raise ResourceNotFoundError("No existe un producto con el ID solicitado")
        return self._a_entidad(producto)

    def actualizar(self, bd: Session, id_producto: str, entidad: Producto, commit: bool = True) -> Producto:
        producto = bd.query(ProductoBD).filter(ProductoBD.id_producto == id_producto).first()
        if producto is None:
            raise ResourceNotFoundError("No existe un producto con el ID solicitado")
        producto.nombre_producto = entidad.nombre_producto
        producto.descripcion = entidad.descripcion
        producto.stock = entidad.stock
        producto.stock_minimo = entidad.stock_minimo
        producto.id_categoria = entidad.id_categoria
        producto.precio = entidad.precio
        producto.fecha_actualizacion = entidad.fecha_actualizacion
        if commit:
            bd.commit()
        return entidad

    def eliminar(self, bd: Session, id_producto: str) -> None:
        producto = bd.query(ProductoBD).filter(ProductoBD.id_producto == id_producto).first()
        if producto is None:
            raise ResourceNotFoundError("No existe un producto con el ID solicitado")

        detalle_asociado = bd.query(DetalleVentaBD.id_detalle).filter(
            DetalleVentaBD.id_producto == id_producto
        ).first()
        if detalle_asociado is not None:
            raise ConflictError(
                "No se puede eliminar el producto porque está asociado a detalles de venta"
            )

        try:
            bd.delete(producto)
            bd.commit()
        except IntegrityError:
            bd.rollback()
            raise ConflictError(
                "No se puede eliminar el producto porque tiene relaciones asociadas"
            )

    def contar_por_categoria(self, bd: Session, id_categoria: str) -> int:
        return bd.query(func.count(ProductoBD.id_producto)).filter(
            ProductoBD.id_categoria == id_categoria
        ).scalar()

    def _a_bd(self, entidad: Producto) -> ProductoBD:
        return ProductoBD(
            id_producto=entidad.id_producto,
            nombre_producto=entidad.nombre_producto,
            descripcion=entidad.descripcion,
            stock=entidad.stock,
            stock_minimo=entidad.stock_minimo,
            id_categoria=entidad.id_categoria,
            precio=entidad.precio,
            fecha_creacion=entidad.fecha_creacion,
            fecha_actualizacion=entidad.fecha_actualizacion,
        )

    def _a_entidad(self, producto: ProductoBD) -> Producto:
        return Producto(
            id_producto=producto.id_producto,
            nombre_producto=producto.nombre_producto,
            descripcion=producto.descripcion,
            stock=producto.stock,
            stock_minimo=producto.stock_minimo,
            id_categoria=producto.id_categoria,
            precio=producto.precio,
            fecha_creacion=producto.fecha_creacion,
            fecha_actualizacion=producto.fecha_actualizacion,
        )


producto_repositorio = ProductoRepositorio()
