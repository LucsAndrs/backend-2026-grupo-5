# Evidencia de pruebas — Minimarket API

Colección ejecutable: [`pruebas.http`](./pruebas.http)

## Cómo ejecutar

Requisitos: `uv`, `curl` y Node.js con `npx` (para ejecutar httpyac).

```bash
bash tests/ejecutar_pruebas.sh
```

El script:

1. Crea una base SQLite temporal en `/tmp/minimarket_pruebas_XXXXXX.db`.
2. Aplica `alembic upgrade head` sobre esa base.
3. Levanta la API en un puerto libre.
4. Ejecuta los 46 requests de `pruebas.http` con `httpyac`.
5. Guarda la salida en `tests/evidencia/ejecucion-<fecha>.log`.
6. Detiene la API y elimina la base temporal.

También se puede ejecutar la colección contra una API ya levantada:

```bash
npx --yes httpyac send tests/pruebas.http --all --no-color --var baseUrl=http://localhost:8001
```

La colección está diseñada para httpyac (las aserciones `??` son específicas de esa herramienta). El archivo `tests/http-client.env.json` define los entornos `docker` (`8001`) y `pruebas` (`8002`) para cambiar la URL base sin editar el archivo.

## Aislamiento y restablecimiento de datos

- **Aislamiento:** el script usa una base SQLite exclusiva para pruebas, distinta de `minimarket.db` y del volumen de PostgreSQL de Docker. No modifica datos de desarrollo.
- **Restablecimiento:** la base temporal se crea desde cero en cada ejecución y se elimina al terminar mediante un `trap`, incluso si hay errores.
- **Repetibilidad:** los nombres de categorías y productos usan la variable `{{$sufijo}}` (`{{$timestamp}}`), por lo que no chocan si la colección se ejecuta varias veces contra una base persistente.
- **Limpieza:** los casos 1 a 7 eliminan los recursos que crean. El caso 8 deja una venta pagada porque la API prohíbe eliminarla (`409`); en la ejecución aislada desaparece al borrar la base temporal. Si se ejecuta contra el PostgreSQL de Docker y se quiere restablecer todo: `docker compose down -v && docker compose up --build`.

## Resultado de la ejecución

Ejecución registrada: **2026-10-31 20:22:05**.

- **46 requests procesados**
- **46 exitosos**
- **0 fallidos**

Distribución de códigos HTTP: `200` ×10, `201` ×16, `204` ×12, `400` ×3, `404` ×3, `409` ×1, `422` ×1.

Log completo: [`evidencia/ejecucion-20261031-202205.log`](./evidencia/ejecucion-20261031-202205.log)

| # | Caso | Entrada | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- | --- |
| 1 | CRUD de categoría | `POST /categorias/` con nombre único; `GET`, `PATCH` (`descripcion`, `activa=false`) y `DELETE`; `GET` posterior | `201`, `200`, `200`, `204`, `404` | `201`, `200` (`cantidad_productos=0`), `200` (descripción actualizada), `204`, `404` con `RESOURCE_NOT_FOUND` |
| 2 | CRUD de producto | Categoría auxiliar; `POST /productos/` con stock 10 y precio 1500; `GET`; `PATCH` stock 7; `DELETE`; `GET` posterior | `201`, `200`, `200` con stock 7, `204`, `404` | `201`, `200` (stock 10, precio 1500), `200` (stock 7), `204`, `404` con `RESOURCE_NOT_FOUND` |
| 3 | Validación inválida | `POST /productos/` con body `{}` | `422` con `VALIDATION_ERROR` y detalles | `422` con `VALIDATION_ERROR` y `details.length > 0` |
| 4 | Recurso inexistente | `GET /categorias/00000000-0000-0000-0000-000000000000` | `404` con `RESOURCE_NOT_FOUND` | `404` con `RESOURCE_NOT_FOUND` |
| 5 | Regla de negocio: stock | Producto con stock 1; venta con cantidad 2 | `400` con `BUSINESS_RULE_VIOLATION` | `400` con `BUSINESS_RULE_VIOLATION`; no se creó la venta |
| 6 | Filtro, orden y paginación | 3 productos con precios 100, 300 y 200; `GET /productos/?nombre=Filtro-<sufijo>&ordenar_por=precio&direccion=desc&pagina=1&limite=2` y página 2 | Página 1: `total=3`, `total_paginas=2`, precios `[300, 200]`; página 2: precio `[100]` | Página 1: `200`, `total=3`, `total_paginas=2`, `items.length=2`, precios `[300, 200]`; página 2: `200`, `items.length=1`, precio `[100]` |
| 7 | Persistencia de datos | Crear categoría, producto y venta (2 × 1000); `GET /ventas/{id}`; `GET /ventas/{id}/boleta`; `DELETE` venta | `201`; `200` con total 2000 y 1 detalle; `200` boleta; `204` | `201`; `200` con `total=2000` y `detalles.length=1`; `200` boleta con `total=2000`; `204` |
| 8 | Reglas de pago y conflicto | Venta con total 100; pago de 50; pago de 100; segundo pago de 100; `GET /pagos/{id}`; `GET /ventas/{id}`; `DELETE /ventas/{id}` | `400`; `201` exitoso; `400`; `200`; `200` con pago; `409` | `400` (`BUSINESS_RULE_VIOLATION`); `201` con `estado_pago=exitoso`; `400` (`BUSINESS_RULE_VIOLATION`); `200`; `200` con `pago.estado_pago=exitoso`; `409` (`CONFLICT`) |

## Cobertura solicitada

| Requisito | Caso(s) |
| --- | --- |
| Operaciones CRUD | 1 y 2 |
| Validación inválida | 3 |
| Recurso inexistente | 4 |
| Regla de negocio | 5 y 8 |
| Consulta con filtro/orden/paginación | 6 |
| Persistencia de datos | 7 |
