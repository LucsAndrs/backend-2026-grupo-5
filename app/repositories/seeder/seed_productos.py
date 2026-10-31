from datetime import datetime

from sqlalchemy.orm import Session

from app.models.categoria_bd import CategoriaBD
from app.models.producto_bd import ProductoBD


PRODUCTOS = [
    ("demo-arroz", "Arroz grano largo", "Arroz grano largo, bolsa de 1 kg.", 40, 8, "Abarrotes", 1200),
    ("demo-jugo", "Jugo de naranja", "Jugo de naranja, envase de 1 litro.", 30, 6, "Bebidas", 2200),
]


def seedear_productos(bd: Session) -> int:
    categorias = {
        categoria.nombre_categoria.casefold(): categoria.id_categoria
        for categoria in bd.query(CategoriaBD).all()
    }
    faltantes = sorted({fila[5] for fila in PRODUCTOS if fila[5].casefold() not in categorias})
    if faltantes:
        raise ValueError(f"Primero ejecuta el seeder de categorías. Faltan: {faltantes}")

    nombres_existentes = {
        nombre.casefold()
        for (nombre,) in bd.query(ProductoBD.nombre_producto).all()
    }
    existentes_ids = {p.id_producto for p in bd.query(ProductoBD.id_producto).all()}
    ahora = datetime.now()
    nuevos = [
        ProductoBD(
            id_producto=id_producto,
            nombre_producto=nombre,
            descripcion=descripcion,
            stock=stock,
            stock_minimo=stock_minimo,
            id_categoria=categorias[categoria.casefold()],
            precio=precio,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
        )
        for id_producto, nombre, descripcion, stock, stock_minimo, categoria, precio in PRODUCTOS
        if nombre.casefold() not in nombres_existentes and id_producto not in existentes_ids
    ]
    bd.add_all(nuevos)
    bd.flush()
    return len(nuevos)
