"""Comprueba que dos pagos simultáneos sobre una venta no duplican el pago."""

import json
import sys
import threading
import uuid
from urllib import error, request


BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")


def llamar(metodo: str, ruta: str, cuerpo: dict | None = None) -> tuple[int, dict | None]:
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    cabeceras = {"Content-Type": "application/json"} if datos else {}
    peticion = request.Request(
        f"{BASE_URL}{ruta}", data=datos, headers=cabeceras, method=metodo
    )
    try:
        with request.urlopen(peticion, timeout=30) as respuesta:
            texto = respuesta.read().decode("utf-8")
            return respuesta.status, json.loads(texto) if texto else None
    except error.HTTPError as exc:
        texto = exc.read().decode("utf-8")
        return exc.code, json.loads(texto) if texto else None


def crear(metodo: str, ruta: str, cuerpo: dict, esperado: int) -> dict:
    estado, respuesta = llamar(metodo, ruta, cuerpo)
    if estado != esperado or respuesta is None:
        raise AssertionError(f"{metodo} {ruta}: esperado {esperado}, obtenido {estado}")
    return respuesta


def main() -> None:
    sufijo = uuid.uuid4().hex[:8]
    categoria = crear(
        "POST",
        "/categorias/",
        {
            "nombre_categoria": f"Categoria Concurrencia {sufijo}",
            "descripcion": "Prueba de pagos simultáneos",
            "activa": True,
        },
        201,
    )
    producto = crear(
        "POST",
        "/productos/",
        {
            "nombre_producto": f"Producto Concurrencia {sufijo}",
            "descripcion": "Prueba de pagos simultáneos",
            "stock": 5,
            "stock_minimo": 1,
            "id_categoria": categoria["id_categoria"],
            "precio": 100,
        },
        201,
    )
    venta = crear(
        "POST",
        "/ventas",
        {
            "cliente": f"Cliente Concurrencia {sufijo}",
            "detalles": [
                {"id_producto": producto["id_producto"], "cantidad_producto": 1}
            ],
        },
        201,
    )
    id_venta = venta["id_venta"]
    pago = {"id_venta": id_venta, "monto": venta["total"], "metodo_pago": "debito"}

    barrera = threading.Barrier(2)
    resultados: list[tuple[int, dict | None]] = []
    errores: list[Exception] = []

    def pagar() -> None:
        try:
            barrera.wait(timeout=10)
            resultados.append(llamar("POST", "/pagos", pago))
        except Exception as exc:  # se reporta al final con detalle
            errores.append(exc)

    hilos = [threading.Thread(target=pagar) for _ in range(2)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join(timeout=30)

    if any(hilo.is_alive() for hilo in hilos):
        raise AssertionError("Los pagos simultáneos no terminaron a tiempo")
    if errores:
        raise AssertionError(f"Error en pagos simultáneos: {errores!r}")
    if len(resultados) != 2:
        raise AssertionError(f"Se esperaban 2 respuestas, se obtuvieron {len(resultados)}")

    codigos = sorted(estado for estado, _ in resultados)
    if codigos != [201, 409]:
        raise AssertionError(f"Códigos esperados [201, 409], obtenidos {codigos}")

    conflicto = next(respuesta for estado, respuesta in resultados if estado == 409)
    if conflicto is None or conflicto.get("error", {}).get("code") != "CONFLICT":
        raise AssertionError("El rechazo debe ser 409 CONFLICT")

    estado, pagos = llamar("GET", "/pagos")
    if estado != 200 or pagos is None:
        raise AssertionError(f"GET /pagos devolvió {estado}")
    exitosos = [
        registro
        for registro in pagos
        if registro["id_venta"] == id_venta and registro["estado_pago"] == "exitoso"
    ]
    if len(exitosos) != 1:
        raise AssertionError(f"Se persistieron {len(exitosos)} pagos exitosos")

    print(f"CONCURRENCIA: 201 + 409; un pago exitoso persistido para {id_venta}")


if __name__ == "__main__":
    main()
