# Evidencia de pruebas — Minimarket API

Colección ejecutable: [`pruebas.http`](./pruebas.http)

Verificación de pagos simultáneos: [`verificar_concurrencia_pagos.py`](./verificar_concurrencia_pagos.py)

## Cómo ejecutar

Requisitos: `uv`, `curl` y Node.js con `npx` (para ejecutar httpyac).

```bash
bash tests/ejecutar_pruebas.sh
```

El script:

1. Crea una base SQLite temporal en `/tmp/minimarket_pruebas_XXXXXX.db`.
2. Aplica `alembic upgrade head`, incluido el índice único parcial de pagos.
3. Levanta la API en un puerto libre.
4. Ejecuta los 52 requests de `pruebas.http` con `httpyac`.
5. Ejecuta `verificar_concurrencia_pagos.py`: dos `POST /pagos` simultáneos sobre la misma venta; espera `201` y `409` y comprueba que solo quede un pago exitoso.
6. Guarda la salida en `tests/evidencia/ejecucion-<fecha>.log`.
7. Detiene la API y elimina la base temporal.

También se puede ejecutar la colección contra una API ya levantada:

```bash
npx --yes httpyac send tests/pruebas.http --all --no-color --var baseUrl=http://localhost:8001
python tests/verificar_concurrencia_pagos.py http://localhost:8001
```

La colección está diseñada para httpyac (las aserciones `??` son específicas de esa herramienta). El archivo `tests/http-client.env.json` define los entornos `docker` (`8001`) y `pruebas` (`8002`) para cambiar la URL base sin editar el archivo.

> Nota de entorno: en este equipo Windows, `bash tests/ejecutar_pruebas.sh` terminó con error real por CRLF y rutas POSIX (`.venv/bin`). La ejecución registrada abajo replicó los mismos pasos desde PowerShell con rutas Windows y la misma base SQLite aislada; el fallo del script original no se ocultó ni se maquilló.

## Aislamiento y restablecimiento de datos

- **Aislamiento:** el script usa una base SQLite exclusiva para pruebas, distinta de `minimarket.db` y del volumen de PostgreSQL de Docker. No modifica datos de desarrollo.
- **Restablecimiento:** la base temporal se crea desde cero en cada ejecución y se elimina al terminar, incluso si hay errores.
- **Repetibilidad:** los nombres de categorías y productos usan `{{$timestamp}}`; la prueba de concurrencia usa un UUID corto.
- **Limpieza:** los casos 1 a 7 eliminan los recursos que crean. El caso 8 deja una venta pagada porque la API prohíbe eliminarla (`409`); en la ejecución aislada desaparece al borrar la base temporal. Si se ejecuta contra PostgreSQL de Docker y se quiere restablecer todo: `docker compose down -v && docker compose up --build`.

## Resultado de la ejecución

Ejecución registrada: **2026-11-25 21:26:36**.

- **52 requests httpyac procesados**
- **52 exitosos**
- **0 fallidos**
- **Concurrencia:** 1 pago `201`, 1 pago `409 CONFLICT`, 1 pago exitoso persistido para la venta `1b88a49a-aaa6-4abe-82bc-0db1e933aa14`.

Distribución de códigos HTTP de la colección httpyac (no incluye los dos requests de la verificación de concurrencia): `200` ×11, `201` ×16, `204` ×12, `400` ×2, `404` ×5, `409` ×2, `422` ×4.

Log completo: [`evidencia/ejecucion-20261125-212636.log`](./evidencia/ejecucion-20261125-212636.log)

| # | Caso | Entrada | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- | --- |
| 1 | CRUD de categoría | `POST /categorias/` con nombre único; `GET`, `PATCH` y `DELETE`; `GET` posterior | `201`, `200`, `200`, `204`, `404` | `201`, `200`, `200`, `204`, `404` con `RESOURCE_NOT_FOUND` |
| 2 | CRUD de producto | Categoría auxiliar; `POST/GET/PATCH/DELETE` de producto; `GET` posterior | `201`, `200`, `200`, `204`, `404` | `201`, `200`, `200`, `204`, `404` con `RESOURCE_NOT_FOUND` |
| 3 | Validación inválida | `POST /productos/` con `{}` | `422 VALIDATION_ERROR` con detalles | `422 VALIDATION_ERROR` con `details.length > 0` |
| 4 | Recurso inexistente | `GET` de categoría inexistente | `404 RESOURCE_NOT_FOUND` | `404 RESOURCE_NOT_FOUND` |
| 5 | Regla de negocio: stock | Producto con stock 1; venta de 2 unidades | `400 BUSINESS_RULE_VIOLATION` | `400 BUSINESS_RULE_VIOLATION` |
| 6 | Filtro, orden y paginación | 3 productos; `ordenar_por=precio&direccion=desc&limite=2` | Páginas `[300, 200]` y `[100]` | Páginas `[300, 200]` y `[100]` |
| 7 | Persistencia de datos | Crear categoría, producto y venta; `GET` venta y boleta | `201`; `200`; `200`; `204` | `201`; `200` con total 2000; `200`; `204` |
| 8 | Reglas de pago | Venta de 100; pago de 50; pago de 100; segundo pago; `GET /pagos/{id}`; `GET /ventas/{id}`; `DELETE /ventas/{id}` | `400`; `201`; `409`; `200`; `200`; `409` | `400 BUSINESS_RULE_VIOLATION`; `201` exitoso; `409 CONFLICT`; `200`; `200` con pago; `409 CONFLICT` |
| 9 | Validaciones adicionales de pago | Venta inexistente, monto negativo, método inválido, ID vacío, listado, pago inexistente | `404`; `422`; `422`; `422`; `200`; `404` | `404`; `422`; `422`; `422`; `200`; `404` |

## Cobertura solicitada

| Requisito | Caso(s) |
| --- | --- |
| Operaciones CRUD | 1 y 2 |
| Validación inválida | 3 y 9 |
| Recurso inexistente | 4 y 9 |
| Regla de negocio | 5, 8 y 9 |
| Consulta con filtro/orden/paginación | 6 |
| Persistencia de datos | 7 |
| Pago duplicado secuencial | 8 |
| Pago duplicado simultáneo | Verificación de concurrencia |
