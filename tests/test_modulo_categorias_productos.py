import os
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configurar BD SQLite en memoria antes de importar la app
os.environ["DATABASE_URL"] = "sqlite://"

from app.base_datos import Base, obtener_bd  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
import app.models  # noqa: E402,F401
import app.models.categoria_modelos  # noqa: E402,F401
import app.models.producto_modelos  # noqa: E402,F401
import app.models.detalle_venta_modelos  # noqa: E402,F401
import app.models.venta_modelos  # noqa: E402,F401
import app.models.pago_modelos  # noqa: E402,F401


@pytest.fixture()
def cliente():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SesionPrueba = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    Base.metadata.create_all(bind=motor)

    def override_obtener_bd():
        bd = SesionPrueba()
        try:
            yield bd
        finally:
            bd.close()

    fastapi_app.dependency_overrides[obtener_bd] = override_obtener_bd
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=motor)
    motor.dispose()


def crear_categoria(cliente, nombre="Bebidas", descripcion="Bebidas frías", activa=True):
    resp = cliente.post(
        "/categorias/",
        json={
            "nombre_categoria": nombre,
            "descripcion": descripcion,
            "activa": activa,
        },
    )
    return resp


def crear_producto(cliente, id_categoria, **overrides):
    payload = {
        "nombre_producto": "Agua",
        "descripcion": "Agua mineral",
        "stock": 10,
        "stock_minimo": 2,
        "id_categoria": id_categoria,
        "precio": 1000,
    }
    payload.update(overrides)
    return cliente.post("/productos/", json=payload)


def crear_venta_con_producto(cliente, id_producto, cantidad=1):
    return cliente.post(
        "/ventas",
        json={
            "cliente": "Cliente Test",
            "detalles": [
                {
                    "id_producto": id_producto,
                    "cantidad_producto": cantidad,
                }
            ],
        },
    )


class TestProductos:
    def test_crear_producto_valido(self, cliente):
        cat = crear_categoria(cliente).json()
        resp = crear_producto(cliente, cat["id_categoria"])

        assert resp.status_code == 201
        body = resp.json()
        assert body["nombre_producto"] == "Agua"
        assert body["descripcion"] == "Agua mineral"
        assert body["stock"] == 10
        assert body["stock_minimo"] == 2
        assert body["id_categoria"] == cat["id_categoria"]
        assert body["precio"] == 1000
        assert "id_producto" in body
        assert "fecha_creacion" in body
        assert "fecha_actualizacion" in body

    @pytest.mark.parametrize(
        "campo,valor",
        [("precio", -1), ("stock", -1), ("stock_minimo", -1)],
    )
    def test_rechazar_valores_negativos_creacion(self, cliente, campo, valor):
        cat = crear_categoria(cliente).json()
        resp = crear_producto(cliente, cat["id_categoria"], **{campo: valor})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_rechazar_nombre_vacio_creacion(self, cliente):
        cat = crear_categoria(cliente).json()
        resp = crear_producto(cliente, cat["id_categoria"], nombre_producto="   ")
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.parametrize(
        "campo,valor",
        [
            ("precio", -5),
            ("stock", -3),
            ("stock_minimo", -2),
            ("nombre_producto", "  "),
            ("descripcion", ""),
        ],
    )
    def test_rechazar_datos_invalidos_actualizacion(self, cliente, campo, valor):
        cat = crear_categoria(cliente).json()
        prod = crear_producto(cliente, cat["id_categoria"]).json()
        resp = cliente.patch(f"/productos/{prod['id_producto']}", json={campo: valor})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_eliminar_producto_sin_relaciones(self, cliente):
        cat = crear_categoria(cliente).json()
        prod = crear_producto(cliente, cat["id_categoria"]).json()
        resp = cliente.delete(f"/productos/{prod['id_producto']}")
        assert resp.status_code == 204

        get_resp = cliente.get(f"/productos/{prod['id_producto']}")
        assert get_resp.status_code == 404

    def test_rechazar_eliminar_producto_asociado_a_detalle_venta(self, cliente):
        cat = crear_categoria(cliente).json()
        prod = crear_producto(cliente, cat["id_categoria"], stock=5).json()
        venta_resp = crear_venta_con_producto(cliente, prod["id_producto"], cantidad=1)
        assert venta_resp.status_code == 201

        resp = cliente.delete(f"/productos/{prod['id_producto']}")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "CONFLICT"

        get_resp = cliente.get(f"/productos/{prod['id_producto']}")
        assert get_resp.status_code == 200


class TestCategorias:
    def test_crear_categoria_valida(self, cliente):
        resp = crear_categoria(cliente)
        assert resp.status_code == 201
        body = resp.json()
        assert body["nombre_categoria"] == "Bebidas"
        assert body["descripcion"] == "Bebidas frías"
        assert body["activa"] is True
        assert "id_categoria" in body
        assert "fecha_creacion" in body
        assert "fecha_actualizacion" in body
        assert body["cantidad_productos"] == 0

    def test_rechazar_nombre_vacio_creacion(self, cliente):
        resp = crear_categoria(cliente, nombre="   ")
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.parametrize(
        "campo,valor",
        [("nombre_categoria", " "), ("descripcion", "")],
    )
    def test_rechazar_datos_invalidos_actualizacion(self, cliente, campo, valor):
        cat = crear_categoria(cliente).json()
        resp = cliente.patch(f"/categorias/{cat['id_categoria']}", json={campo: valor})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_eliminar_categoria_sin_productos(self, cliente):
        cat = crear_categoria(cliente).json()
        resp = cliente.delete(f"/categorias/{cat['id_categoria']}")
        assert resp.status_code == 204

        get_resp = cliente.get(f"/categorias/{cat['id_categoria']}")
        assert get_resp.status_code == 404

    def test_rechazar_eliminar_categoria_con_productos(self, cliente):
        cat = crear_categoria(cliente).json()
        prod_resp = crear_producto(cliente, cat["id_categoria"])
        assert prod_resp.status_code == 201

        resp = cliente.delete(f"/categorias/{cat['id_categoria']}")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "CONFLICT"

        get_resp = cliente.get(f"/categorias/{cat['id_categoria']}")
        assert get_resp.status_code == 200


class TestDTOResponses:
    def test_post_producto_devuelve_producto_response(self, cliente):
        cat = crear_categoria(cliente).json()
        resp = crear_producto(cliente, cat["id_categoria"])
        assert resp.status_code == 201
        body = resp.json()
        expected_keys = {
            "id_producto",
            "nombre_producto",
            "descripcion",
            "stock",
            "stock_minimo",
            "id_categoria",
            "precio",
            "fecha_creacion",
            "fecha_actualizacion",
        }
        assert set(body.keys()) == expected_keys

    def test_post_categoria_devuelve_categoria_response(self, cliente):
        resp = crear_categoria(cliente)
        assert resp.status_code == 201
        body = resp.json()
        expected_keys = {
            "id_categoria",
            "nombre_categoria",
            "descripcion",
            "activa",
            "fecha_creacion",
            "fecha_actualizacion",
            "cantidad_productos",
        }
        assert set(body.keys()) == expected_keys
