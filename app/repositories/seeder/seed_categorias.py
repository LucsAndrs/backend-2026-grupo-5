import uuid

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.categoria_bd import CategoriaBD


CATEGORIAS = [
    ("Abarrotes", "Alimentos envasados y productos de despensa."),
    ("Bebidas", "Bebidas y productos para beber."),
    ("Lácteos", "Leche, quesos, yogures y otros productos lácteos."),
    ("Aseo y limpieza", "Productos de higiene y limpieza del hogar."),
    ("Frutas y verduras", "Frutas y verduras frescas."),
]


def seedear_categorias(bd: Session) -> int:
    existentes = {
        nombre.casefold()
        for (nombre,) in bd.query(CategoriaBD.nombre_categoria).all()
    }
    ahora = datetime.now()
    nuevas = [
        CategoriaBD(
            id_categoria = str(uuid.uuid4()),
            nombre_categoria=nombre,
            descripcion=descripcion,
            activa=True,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
        )
        for nombre, descripcion in CATEGORIAS
        if nombre.casefold() not in existentes
    ]
    bd.add_all(nuevas)
    bd.flush()
    return len(nuevas)
