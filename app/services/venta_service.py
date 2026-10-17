import math
import uuid
from app.domain.venta import Venta
from app.domain.detalleventa import DetalleVenta
from app.schemas.venta_schemas import VentaCreada, VentaRespuesta
from app.excepciones import BusinessRuleError, ConflictError, ResourceNotFoundError
from app.schemas.common import PaginatedResponse
from app.schemas.pago_schemas import PagoResponse
from app.schemas.detalle_venta_create import DetalleVentaResponse
from datetime import date

from app.repositories.product_repository import product_repository
from app.repositories.venta_repository import venta_repositorio
from app.repositories.pago_repository import pago_repositorio

class VentaServicio:
    def __init__(self):
        self.CAMPOS_ORDEN = {"cliente", "total", "fecha_venta"}

    def calcular_total(self, venta: Venta):
        total = 0.0
        for detalle in venta.detalles:
            total = total + detalle.subtotal
        venta.total = total
        return total

    def a_venta_out(self, venta: Venta) -> VentaRespuesta:
        pagos = pago_repositorio.obtener_por_venta(venta.id_venta)
        ultimo_pago = pagos[-1] if pagos else None

        pago_out = None
        if ultimo_pago:
            pago_out = PagoResponse.model_validate(ultimo_pago, from_attributes=True)

        detalles_out = []
        for d in venta.detalles:
            detalles_out.append(
                DetalleVentaResponse.model_validate(d, from_attributes=True)
            )

        return VentaRespuesta(
            id_venta= venta.id_venta,
            fecha_venta= venta.fecha_venta,
            cliente= venta.cliente,
            total= venta.total,
            detalles= detalles_out,
            pago= pago_out,
        )

    def agregar_detalle(self, venta: Venta, detalle: DetalleVenta):
        if detalle.cantidad_producto <= 0:
            raise BusinessRuleError("La cantidad de producto debe ser mayor a cero")
        venta.detalles.append(detalle)
        self.calcular_total(venta)

    def crear_venta(self, datos: VentaCreada):
        venta = Venta(cliente=datos.cliente, fecha_venta=date.today())

        productos_validados = []
        canntidades_acumuladas = {}

        for detalle_data in datos.detalles:
            if detalle_data.cantidad_producto <= 0:
                raise BusinessRuleError("La cantidad de producto debe ser mayor a cero")

            producto = product_repository.get_by_id(detalle_data.id_producto)
            acumulado = canntidades_acumuladas.get(producto.id, 0) + detalle_data.cantidad_producto

            if acumulado > producto.stock:
                raise BusinessRuleError(
                    f"Stock insuficiente para '{producto.name}':"
                    f" Disponible '{producto.stock}', solicitado'{acumulado}'"
                )
            canntidades_acumuladas[producto.id] = acumulado
            productos_validados.append((producto, detalle_data))

        for producto, detalle_data in productos_validados:
            producto = product_repository.get_by_id(producto.id)
            detalle = DetalleVenta(
                id_detalle= str(uuid.uuid4()),
                id_producto= producto.id,
                id_venta= venta.id_venta,
                cantidad_producto= detalle_data.cantidad_producto,
                precio_unitario= producto.price,
                subtotal= detalle_data.cantidad_producto * producto.price,
                iva= 0.0,
                descuento= 0.0,
            )
            self.agregar_detalle(venta, detalle)
            producto.stock -= detalle_data.cantidad_producto
            product_repository.update(producto.id, producto)

        venta_guardada = venta_repositorio.crear_venta(venta)
        return self.a_venta_out(venta_guardada)

    def obtener_venta(self, id_venta: str):
        venta = venta_repositorio.obtener_por_id(id_venta)
        return self.a_venta_out(venta)

    def eliminar_venta(self, id_venta: str):
        venta = venta_repositorio.obtener_por_id(id_venta)

        if pago_repositorio.existe_pago_exitoso(id_venta):
            raise ConflictError("No se puede eliminar una venta que ya fue pagada")

        for detalle in venta.detalles:
            try:
                producto = product_repository.get_by_id(detalle.id_producto)
            except ResourceNotFoundError:
                producto = None
                
            if producto is not None:
                producto.stock += detalle.cantidad_producto
                product_repository.update(producto.id, producto)

        return venta_repositorio.eliminar_venta(id_venta)

    def listar_venta(self, cliente: str = None, ordenar_por: str = None, direccion: str = "asc",
                    pagina: int = 1, limite: int = 20):
        if ordenar_por is not None and ordenar_por not in self.CAMPOS_ORDEN:
            raise BusinessRuleError(f"El campo '{ordenar_por}' no es valido para ordenar")
        ventas = venta_repositorio.listar_todas()

        if cliente:
            ventas_filtradas = []
            for v in ventas:
                if v.cliente.lower() == cliente.lower():
                    ventas_filtradas.append(v)
            ventas = ventas_filtradas

        if ordenar_por:
            reverse = direccion == "desc"
            ventas = sorted(ventas, key=lambda v: getattr(v, ordenar_por), reverse=reverse)

        total = len(ventas)
        if total == 0:
            total_paginas = 0
        else:
            total_paginas = math.ceil(total / limite)

        inicio = (pagina - 1) * limite
        fin = inicio + limite
        ventas_pagina = ventas[inicio:fin]
        items = [self.a_venta_out(v) for v in ventas_pagina]

        return PaginatedResponse(
            items= items,
            total= total,
            pagina= pagina,
            limite= limite,
            total_paginas= total_paginas,
        )

    def generar_boleta(self, id_venta: str):
        venta = venta_repositorio.obtener_por_id(id_venta)
        items = []
        for detalle in venta.detalles:
            items.append({
                "producto_id": detalle.id_producto,
                "cantidad": detalle.cantidad_producto,
                "precio_unitario": detalle.precio_unitario,
                "subtotal": detalle.subtotal,
            })

        return {
            "id_venta": venta.id_venta,
            "fecha_venta": venta.fecha_venta.isoformat(),
            "cliente": venta.cliente,
            "items": items,
            "total": venta.total,
        }

venta_servicio = VentaServicio()