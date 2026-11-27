import unittest
from datetime import date, datetime
from unittest.mock import patch

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.base_datos import Base
import app.models.categoria_modelos
import app.models.detalle_venta_modelos
import app.models.pago_modelos
import app.models.producto_modelos
import app.models.venta_modelos

from app.domain.productos import Producto
from app.excepciones import ResourceNotFoundError
from app.models.categoria_modelos import CategoriaBD
from app.models.venta_modelos import VentaBD
from app.repositories.productos_repositorio import producto_repositorio
from app.repositories.venta_repositorio import venta_repositorio
from app.schemas.detalle_venta_esquema import DetalleVentaCrear
from app.schemas.venta_esquemas import VentaCreada
from app.services.venta_servicio import VentaServicio


class VentaServicioTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.bd = self.Session()
        self.servicio = VentaServicio()

        ahora = datetime.now()
        self.bd.add(CategoriaBD(
            id_categoria="cat-prueba",
            nombre_categoria="Categoria Prueba",
            descripcion="Categoria para pruebas",
            activa=True,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
        ))
        self.bd.commit()

        producto = Producto(
            nombre_producto="Producto Prueba",
            descripcion="Producto para pruebas",
            stock=10,
            stock_minimo=1,
            id_categoria="cat-prueba",
            precio=100,
        )
        producto_repositorio.crear(self.bd, producto)
        self.producto_id = producto.id_producto

    def tearDown(self):
        self.bd.close()
        Base.metadata.drop_all(self.engine)

    def _datos(self, cantidad=1):
        return VentaCreada(
            cliente="Cliente Prueba",
            detalles=[DetalleVentaCrear(id_producto=self.producto_id, cantidad_producto=cantidad)],
        )

    def test_numero_boleta_unico_y_persistido(self):
        primera = self.servicio.crear_venta(self.bd, self._datos())
        segunda = self.servicio.crear_venta(self.bd, self._datos())

        self.assertTrue(primera.numero_boleta.startswith("BOL-"))
        self.assertNotEqual(primera.numero_boleta, segunda.numero_boleta)
        self.assertEqual(primera.total, 100)

        boleta = self.servicio.generar_boleta(self.bd, primera.id_venta)
        self.assertEqual(boleta.numero_boleta, primera.numero_boleta)

        recuperada = self.servicio.obtener_venta(self.bd, primera.id_venta)
        self.assertEqual(recuperada.numero_boleta, primera.numero_boleta)

    def test_rollback_stock_cuando_falla_antes_del_commit(self):
        with patch.object(venta_repositorio, "crear_venta", side_effect=RuntimeError("fallo forzado")):
            with self.assertRaises(RuntimeError):
                self.servicio.crear_venta(self.bd, self._datos())

        self.bd.expire_all()
        producto = producto_repositorio.obtener_por_id(self.bd, self.producto_id)
        self.assertEqual(producto.stock, 10)

    def test_reintenta_si_la_base_reporta_numero_boleta_duplicado(self):
        original = venta_repositorio.crear_venta
        llamadas = {"total": 0}
        error = IntegrityError(
            "INSERT INTO ventas",
            {},
            Exception("UNIQUE constraint failed: ventas.numero_boleta"),
        )

        def crear_con_colision(bd, venta, commit=True):
            llamadas["total"] += 1
            if llamadas["total"] == 1:
                raise error
            return original(bd, venta, commit=commit)

        with patch.object(venta_repositorio, "crear_venta", side_effect=crear_con_colision):
            creada = self.servicio.crear_venta(self.bd, self._datos())

        self.assertEqual(llamadas["total"], 2)
        self.assertTrue(venta_repositorio.existe_numero_boleta(self.bd, creada.numero_boleta))

    def test_lee_venta_sin_detalles(self):
        venta_bd = VentaBD(
            id_venta="venta-sin-detalles",
            cliente="Cliente Sin Detalles",
            fecha_venta=date.today(),
            numero_boleta="BOL-20260101-SINDETALLE",
            total=0.0,
        )
        self.bd.add(venta_bd)
        self.bd.commit()

        venta = venta_repositorio.obtener_por_id(self.bd, "venta-sin-detalles")
        self.assertEqual(venta.numero_boleta, "BOL-20260101-SINDETALLE")
        self.assertEqual(venta.detalles, [])

    def test_eliminar_venta_devuelve_stock(self):
        creada = self.servicio.crear_venta(self.bd, self._datos(cantidad=3))

        self.servicio.eliminar_venta(self.bd, creada.id_venta)

        producto = producto_repositorio.obtener_por_id(self.bd, self.producto_id)
        self.assertEqual(producto.stock, 10)
        with self.assertRaises(ResourceNotFoundError):
            venta_repositorio.obtener_por_id(self.bd, creada.id_venta)

    def test_cliente_no_vacio_en_schema(self):
        with self.assertRaises(ValidationError):
            VentaCreada(
                cliente="   ",
                detalles=[DetalleVentaCrear(id_producto=self.producto_id, cantidad_producto=1)],
            )


if __name__ == "__main__":
    unittest.main()
