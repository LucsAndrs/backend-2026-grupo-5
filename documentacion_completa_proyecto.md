# Documentación completa del proyecto — Minimarket API

Documento NotebookLM del estado actual. Incluye el contenido íntegro de archivos textuales de fuente, configuración y pruebas. Se excluyen .env real, binarios, cachés y logs generados. Se redactan las credenciales de ejemplo.

## 1. Resumen ejecutivo y visión general

Backend REST para gestionar categorías, productos, inventario, ventas, detalles de venta y pagos de un minimarket. Valida solicitudes, aplica reglas de negocio y persiste en una base relacional.

Stack: Python >=3.14, FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic, PostgreSQL 16, Psycopg, SQLite local, uv, Docker Compose, Adminer, httpyac para pruebas.

| Dependencia | Restricción pyproject | Versión bloqueada |
| --- | --- | --- |
| `alembic` | `alembic>=1.20.1` | `1.20.1` |
| `fastapi` | `fastapi>=0.141.1` | `0.141.1` |
| `psycopg` | `psycopg[binary]>=3.3.6` | `3.3.6` |
| `pydantic` | `pydantic>=2.13.5` | `2.13.5` |
| `sqlalchemy` | `sqlalchemy>=2.1.5` | `2.1.5` |
| `uvicorn` | `uvicorn>=0.52.4` | `0.52.4` |

## 2. Arquitectura y estructura del proyecto

### Archivos textuales del proyecto

- `.dockerignore`
- `.env.example`
- `.gitignore`
- `.python-version`
- `README.md`
- `alembic.ini`
  - `app/__init__.py`
  - `app/base_datos.py`
    - `app/domain/categorias.py`
    - `app/domain/detalleventa.py`
    - `app/domain/pago.py`
    - `app/domain/productos.py`
    - `app/domain/venta.py`
  - `app/excepciones.py`
  - `app/main.py`
    - `app/models/__init__.py`
    - `app/models/categoria_modelos.py`
    - `app/models/detalle_venta_modelos.py`
    - `app/models/pago_modelos.py`
    - `app/models/producto_modelos.py`
    - `app/models/venta_modelos.py`
    - `app/repositories/categorias_repositorio.py`
    - `app/repositories/detalle_venta_repositorio.py`
    - `app/repositories/pago_repositorio.py`
    - `app/repositories/productos_repositorio.py`
      - `app/repositories/seeder/__init__.py`
      - `app/repositories/seeder/seed_categorias.py`
      - `app/repositories/seeder/seed_detalles_ventas.py`
      - `app/repositories/seeder/seed_pagos.py`
      - `app/repositories/seeder/seed_productos.py`
      - `app/repositories/seeder/seed_todos.py`
      - `app/repositories/seeder/seed_ventas.py`
    - `app/repositories/venta_repositorio.py`
    - `app/routers/categorias_routers.py`
    - `app/routers/detalle_venta_ruta.py`
    - `app/routers/pago_ruta.py`
    - `app/routers/productos_routers.py`
    - `app/routers/venta_router.py`
    - `app/schemas/categorias_schemas.py`
    - `app/schemas/common.py`
    - `app/schemas/detalle_venta_esquema.py`
    - `app/schemas/pago_schemas.py`
    - `app/schemas/productos_schemas.py`
    - `app/schemas/venta_esquemas.py`
    - `app/services/categorias_service.py`
    - `app/services/detalle_venta_servicio.py`
    - `app/services/pago_servicio.py`
    - `app/services/productos_service.py`
    - `app/services/venta_servicio.py`
- `compose.yml`
  - `migrations/env.py`
  - `migrations/script.py.mako`
    - `migrations/versions/d558a2aa70ae_crear_esquema_inicial.py`
- `pyproject.toml`
  - `tests/EVIDENCIA.md`
  - `tests/ejecutar_pruebas.sh`
  - `tests/http-client.env.json`
  - `tests/pruebas.http`
- `uv.lock`

Capas: routers gestionan HTTP; schemas validan DTOs; services aplican reglas; repositories consultan y convierten; models mapean tablas; domain contiene entidades; Alembic versiona esquema; seeders cargan datos demo.

### Flujo de datos

Cliente → Uvicorn/FastAPI → Router → Schema Pydantic y Session → Servicio → Repositorio → Modelo ORM → PostgreSQL o SQLite. El repositorio convierte resultados ORM a dominio; el servicio arma salida; FastAPI responde JSON. Errores pasan por handlers globales.

```mermaid
flowchart LR
 A[Cliente] --> B[Uvicorn / FastAPI] --> C[Router]
 C --> D[Schema]
 C --> E[Session SQLAlchemy]
 D --> F[Servicio]
 E --> F --> G[Repositorio] --> H[Modelo ORM] --> I[(PostgreSQL / SQLite)]
 G --> J[Dominio] --> F --> K[JSON de respuesta]
 F -. error .-> L[Handler]
 L --> K
```

### Entidades y base de datos

| Tabla | Datos / relaciones |
| --- | --- |
| categorias | ID, nombre, descripción, activa, fechas; 1:N productos |
| productos | ID, nombre, descripción, existencias, precio, FK categoría; aparece en detalles |
| ventas | ID, cliente, fecha, total; contiene detalles y admite pagos |
| detalles_ventas | FK venta, FK producto, cantidad, subtotal, precio, IVA, descuento |
| pagos | FK venta, fecha, monto, método, estado |
| EstadoPago | Enum pendiente/exitoso/rechazado; almacenado como texto |

Relaciones: Categoría 1:N Producto; Venta 1:N DetalleVenta; Producto 1:N DetalleVenta; Venta 1:N Pago. Venta ORM usa cascada para detalles; Pago tiene FK, sin relación ORM bidireccional.

## 3. Lógica de negocio y endpoints / API

URLs: Docker http://localhost:8001; local http://localhost:8000; Swagger /docs; ReDoc /redoc; OpenAPI /openapi.json.

| Método | Ruta | Acción |
| --- | --- | --- |
| POST/GET | /categorias/ | Crear/listar categorías |
| GET/PATCH/DELETE | /categorias/{id_categoria} | Consultar, editar o eliminar |
| POST/GET | /productos/ | Crear/listar productos |
| GET/PATCH/DELETE | /productos/{id_producto} | Consultar, editar o eliminar |
| POST | /ventas | Crear venta, detalles y descontar stock |
| GET | /ventas | Listar/filtrar/ordenar/paginar |
| GET | /ventas/{id_venta} | Venta, detalles y pago opcional |
| GET | /ventas/{id_venta}/boleta | Boleta JSON |
| DELETE | /ventas/{id_venta} | Bloquear si pagada; reponer stock si se elimina |
| GET | /ventas/{id_venta}/detalles | Listar detalles |
| GET | /ventas/{id_venta}/detalles/{id_detalle} | Consultar detalle |
| POST | /pagos | Validar y crear pago |
| GET | /pagos | Listar pagos |
| GET | /pagos/{id_pago} | Consultar pago |

Reglas: evitar nombres duplicados; cantidad positiva y stock suficiente; subtotal cantidad×precio, total suma de subtotales; pago requiere venta existente, monto exacto y no tener otro pago exitoso. El proceso marca exitoso directamente; no hay pasarela externa. Al borrar venta no pagada se repone stock.

Errores uniformes: RESOURCE_NOT_FOUND (404), CONFLICT (409), BUSINESS_RULE_VIOLATION (400), VALIDATION_ERROR (422), HTTP_ERROR (status HTTP). JSON de error contiene code, message y details.

Pruebas: tests/EVIDENCIA.md registra 46 requests exitosos y 0 fallidos con SQLite temporal. Es evidencia guardada, no una prueba ejecutada al generar este documento.

## 4. Código fuente completo

Contenido íntegro de los archivos enumerados, salvo .env real y logs. Credenciales de ejemplo sustituidas por placeholders.


### `.dockerignore`

```text
__pycache__/
.venv/
.env
```


### `.env.example`

```dotenv
POSTGRES_USER=<configurar-en-.env>
POSTGRES_PASSWORD=<configurar-en-.env>
POSTGRES_DB=<configurar-en-.env>
```


### `.gitignore`

```text
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.venv/
.env
*.pyc
.venv/
minimarket.db
*.db
```


### `.python-version`

```text
3.14
```


### `README.md`

````markdown
# Minimarket API — Backend 2026 Grupo 5

API REST de un minimarket (categorías, productos, ventas, detalles y pagos) con **FastAPI**, **SQLAlchemy**, **Alembic** y **PostgreSQL**, organizada por capas.

- Swagger: `http://localhost:8001/docs` · OpenAPI: `http://localhost:8001/openapi.json`
- Adminer: `http://localhost:8080` · PostgreSQL: `localhost:5432`
- Python `>=3.14`, gestor [uv](https://docs.astral.sh/uv/)

## Integrantes y responsabilidades

| Integrante | GitHub | Responsabilidad principal |
| --- | --- | --- |
| Benjamín Alarcón | [@Benjamin-Alarcon](https://github.com/Benjamin-Alarcon) | Estructura inicial; capas y CRUD de categorías/productos; filtros, orden, paginación y relación categoría-producto. |
| Elías Ayuqueo | [@ecayuqueo](https://github.com/ecayuqueo) | Dominio y módulo de ventas; stock, atomicidad, excepciones, Docker, PostgreSQL y Adminer. |
| Lucas Villegas | [@LucsAndrs](https://github.com/LucsAndrs) | Organización de capas; detalle de venta; migraciones Alembic; seeders e integración en `main`. |
| Nicolás Calderón | [@nikitsz](https://github.com/nikitsz) | Dominio de pago, DTOs y módulo de pagos; validaciones y estandarización de nombres. |

## Instalación y ejecución

### Docker (recomendado)

Requisitos: Docker + Compose v2.

```bash
cp .env.example .env
docker compose up --build
```

La API aplica `alembic upgrade head` al arrancar (`compose.yml:25`).

```bash
docker compose ps
docker compose logs -f api
docker compose down      # detener
docker compose down -v   # además borra el volumen de PostgreSQL
```

### Local con uv

Requisitos: Python 3.14 y uv.

```bash
uv sync
export DATABASE_URL="sqlite:///./minimarket.db"   # o PostgreSQL, ver abajo
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

> El proyecto no carga `.env` automáticamente fuera de Docker Compose; exporta las variables en tu shell.

| Servicio | URL |
| --- | --- |
| API (Docker) | `http://localhost:8001` |
| API (local) | `http://localhost:8000` |
| Swagger / ReDoc | `/docs` / `/redoc` |
| Adminer | `http://localhost:8080` |

## Variables de entorno

`.env.example`:

```dotenv
POSTGRES_USER=<configurar-en-.env>
POSTGRES_PASSWORD=<configurar-en-.env>
POSTGRES_DB=<configurar-en-.env>
```

| Variable | Descripción |
| --- | --- |
| `POSTGRES_USER` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Contraseña del usuario. |
| `POSTGRES_DB` | Nombre de la base de datos. |
| `DATABASE_URL` | Conexión SQLAlchemy. Compose la construye como `postgresql+psycopg://USER:PASS@db:5432/DB`. |

Notas: sin `DATABASE_URL`, `app.base_datos` usa `sqlite:///./minimarket.db`; Alembic sí requiere `DATABASE_URL`; `.env` está en `.gitignore`.

## Base de datos

- **PostgreSQL (Docker):** imagen `postgres:16`, volumen `postgres_data` y healthcheck. Desde el host: `postgresql+psycopg://<USER>:<PASSWORD>@localhost:5432/<DB>`.
- **SQLite (local):** `export DATABASE_URL="sqlite:///./minimarket.db"`.
- **Adminer:** sistema `PostgreSQL`, servidor `db` (red Compose) o `localhost` (host), usuario/contraseña/BD según `.env`.

Tablas de la migración inicial:

| Tabla | Contenido |
| --- | --- |
| `categorias` | Categorías y estado activo. |
| `productos` | Productos, stock, precio y FK a categoría. |
| `ventas` | Cabecera: cliente, fecha y total. |
| `detalles_ventas` | Líneas de venta con FK a venta y producto. |
| `pagos` | Pagos asociados a una venta. |

```text
categorias 1─N productos
ventas 1─N detalles_ventas N─1 productos
ventas 1─N pagos
```

## Migraciones y seeders

```bash
# Migraciones (local)
uv run alembic upgrade head
uv run alembic current
uv run alembic history
uv run alembic revision --autogenerate -m "descripcion"
uv run alembic downgrade -1

# Migraciones (Docker)
docker compose exec api alembic upgrade head

# Seeders (idempotentes, en orden de dependencias)
uv run python -m app.repositories.seeder.seed_todos
docker compose exec api python -m app.repositories.seeder.seed_todos
```

`seed_todos` inserta 5 categorías, 2 productos, 2 ventas, 4 detalles y 2 pagos demo. Orden: categorías → productos → ventas → detalles → pagos. También ejecuta `Base.metadata.create_all`; en PostgreSQL se recomienda migrar primero.

## Estructura y capas

```text
app/
├── main.py               # FastAPI, routers y handlers de error
├── base_datos.py         # engine, sesión, Base y obtener_bd
├── excepciones.py        # ApiError y errores de negocio
├── domain/               # entidades puras (dataclasses/enums)
├── schemas/              # DTOs Pydantic de entrada/salida
├── models/               # modelos SQLAlchemy (ORM)
├── repositories/         # consultas y mapeo ORM ↔ dominio
│   └── seeder/           # datos demo
├── services/             # reglas de negocio
└── routers/              # endpoints HTTP
migrations/               # entorno y versiones Alembic
compose.yml  Dockerfile  alembic.ini  pyproject.toml
```

| Capa | Función | No debe hacer |
| --- | --- | --- |
| `routers/` | Endpoints, parámetros, códigos HTTP y `response_model`; inyecta la sesión. | Lógica de negocio ni SQL. |
| `schemas/` | Validar y tipar entrada/salida con Pydantic. | Acceder a la BD. |
| `services/` | Reglas de negocio: stock, totales, pagos, validaciones. | Conocer SQLAlchemy. |
| `repositories/` | Consultas, persistencia y conversión ORM ↔ dominio. | Reglas de negocio complejas. |
| `models/` | Mapeo de tablas y relaciones. | Exponerse directamente en la API. |
| `domain/` | Entidades puras con IDs y valores por defecto. | Depender de FastAPI/Pydantic/SQLAlchemy. |

```text
routers → services → repositories → models → BD
              ↘ schemas        repositories → domain ← services
```

## Recorrido de una solicitud

```mermaid
flowchart LR
    A[Cliente HTTP] --> B[Uvicorn] --> C[FastAPI main.py]
    C --> D[Router] --> E[obtener_bd]
    D --> F[Service] --> G[Repository] --> H[Modelo ORM] --> I[(PostgreSQL/SQLite)]
    G -. convierte .-> J[Entidad de dominio] --> F
    F -. construye .-> K[Schema Pydantic] --> D --> C
    C --> L{¿Excepción?}
    L -- Sí --> M[Handler de error] --> A
    L -- No --> N[response_model JSON] --> A
```

Ejemplo `POST /ventas`: el router valida con `VentaCreada` → el service verifica cantidades, stock y calcula totales → el repository descuenta stock y persiste venta + detalles → el service arma `VentaRespuesta` → el router responde `201`. Si falla una regla, el handler devuelve el sobre de error.

## Contrato REST

Base: `http://localhost:8001` (Docker) o `:8000` (local).

Errores uniformes:

```json
{ "error": { "code": "BUSINESS_RULE_VIOLATION", "message": "...", "details": [] } }
```

| Código | HTTP |
| --- | --- |
| `RESOURCE_NOT_FOUND` | 404 |
| `CONFLICT` | 409 |
| `BUSINESS_RULE_VIOLATION` | 400 |
| `VALIDATION_ERROR` | 422 |
| `HTTP_ERROR` | 404/405/etc. |

| Método | Ruta | Body / respuesta | Códigos |
| --- | --- | --- | --- |
| `POST` | `/categorias/` | `CategoriaCreate` → `Categoria` | 201, 409, 422 |
| `GET` | `/categorias/` | → `PaginatedResponse[CategoriaResponse]` | 200, 400, 422 |
| `GET` | `/categorias/{id_categoria}` | → `CategoriaResponse` | 200, 404 |
| `PATCH` | `/categorias/{id_categoria}` | `CategoriaPatch` → `CategoriaResponse` | 200, 404, 422 |
| `DELETE` | `/categorias/{id_categoria}` | → sin contenido | 204, 404 |
| `POST` | `/productos/` | `ProductoCreate` → `Producto` | 201, 404, 409, 422 |
| `GET` | `/productos/` | → `PaginatedResponse[ProductoResponse]` | 200, 400, 422 |
| `GET` | `/productos/{id_producto}` | → `ProductoResponse` | 200, 404 |
| `PATCH` | `/productos/{id_producto}` | `ProductoPatch` → `ProductoResponse` | 200, 404, 422 |
| `DELETE` | `/productos/{id_producto}` | → sin contenido | 204, 404 |
| `POST` | `/ventas` | `VentaCreada` → `VentaRespuesta` | 201, 400, 404, 422 |
| `GET` | `/ventas` | → `PaginatedResponse[VentaRespuesta]` | 200, 400, 422 |
| `GET` | `/ventas/{id_venta}` | → `VentaRespuesta` | 200, 404 |
| `GET` | `/ventas/{id_venta}/boleta` | → JSON libre | 200, 404 |
| `DELETE` | `/ventas/{id_venta}` | → sin contenido | 204, 404, 409 |
| `GET` | `/ventas/{id_venta}/detalles` | → `list[DetalleVenta]` | 200 |
| `GET` | `/ventas/{id_venta}/detalles/{id_detalle}` | → `DetalleVenta` | 200, 404 |
| `POST` | `/pagos` | `CrearPago` → `PagoRespuesta` | 201, 400, 404, 422 |
| `GET` | `/pagos` | → `list[PagoRespuesta]` | 200 |
| `GET` | `/pagos/{id_pago}` | → `PagoRespuesta` | 200, 404 |

Bodies principales:

```json
// POST /categorias/
{"nombre_categoria":"Abarrotes","descripcion":"Despensa","activa":true}

// POST /productos/
{"nombre_producto":"Arroz","descripcion":"Bolsa 1 kg","stock":10,"stock_minimo":2,"id_categoria":"UUID","precio":1200}

// POST /ventas
{"cliente":"Cliente Demo","detalles":[{"id_producto":"UUID","cantidad_producto":2}]}

// POST /pagos
{"id_venta":"UUID","monto":2400,"metodo_pago":"debito"}
```

Listados: `pagina` (≥1, default 1), `limite` (1–100, default 20), `direccion` (`asc`/`desc`). Categorías: `activa`, `nombre`, `ordenar_por` (default `nombre_categoria`). Productos: `id_categoria`, `nombre`, `ordenar_por` (default `nombre_producto`). Ventas: `cliente`, `ordenar_por` (`cliente`/`total`/`fecha_venta`).

Reglas: cantidad > 0, stock suficiente y acumulado, stock se descuenta al vender y se repone al eliminar, venta pagada no se elimina (409); pago debe existir la venta, monto igual al total y solo un pago exitoso por venta.

## OpenAPI

- Swagger UI: `/docs` · ReDoc: `/redoc` · JSON: `/openapi.json`

```bash
uv run python - <<'PY'
import json
from app.main import app
json.dump(app.openapi(), open("openapi.json", "w"), indent=2, ensure_ascii=False)
PY
```

## Ejecución de pruebas

Hay una colección `.http` con 8 casos: CRUD, validación inválida, recurso inexistente, regla de negocio, filtro/orden/paginación, persistencia y reglas de pago.

- Colección: `tests/pruebas.http`
- Evidencia y explicación del aislamiento: `tests/EVIDENCIA.md`
- Ejecución automatizada sobre SQLite temporal: `tests/ejecutar_pruebas.sh`

```bash
# Base temporal aislada (requiere uv, curl y Node/npx)
bash tests/ejecutar_pruebas.sh

# O contra una API ya levantada
npx --yes httpyac send tests/pruebas.http --all --no-color --var baseUrl=http://localhost:8001
```

No hay suite de `pytest` todavía; si se agrega, se sugiere `TestClient` y sobreescribir `obtener_bd` con SQLite en memoria.

## Notas

- Sin autenticación ni CORS.
- `POST /categorias/` y `POST /productos/` devuelven la entidad de dominio, no el schema `*Response`.
- Categorías/productos usan barra final; ventas/pagos no.
- En Docker la API se publica en `8001` (el contenedor escucha en `8000`).
````


### `alembic.ini`

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts.
# this is typically a path given in POSIX (e.g. forward slashes)
# format, relative to the token %(here)s which refers to the location of this
# ini file
script_location = %(here)s/migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
# Or organize into date-based subdirectories (requires recursive_version_locations = true)
# file_template = %%(year)d/%%(month).2d/%%(day).2d_%%(hour).2d%%(minute).2d_%%(second).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.  for multiple paths, the path separator
# is defined by "path_separator" below.
prepend_sys_path = .


# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the tzdata library which can be installed by adding
# `alembic[tz]` to the pip requirements.
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to <script_location>/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "path_separator"
# below.
# version_locations = %(here)s/bar:%(here)s/bat:%(here)s/alembic/versions

# path_separator; This indicates what character is used to split lists of file
# paths, including version_locations and prepend_sys_path within configparser
# files such as alembic.ini.
# The default rendered in new alembic.ini files is "os", which uses os.pathsep
# to provide os-dependent path splitting.
#
# Note that in order to support legacy alembic.ini files, this default does NOT
# take place if path_separator is not present in alembic.ini.  If this
# option is omitted entirely, fallback logic is as follows:
#
# 1. Parsing of the version_locations option falls back to using the legacy
#    "version_path_separator" key, which if absent then falls back to the legacy
#    behavior of splitting on spaces and/or commas.
# 2. Parsing of the prepend_sys_path option falls back to the legacy
#    behavior of splitting on spaces, commas, or colons.
#
# Valid values for path_separator are:
#
# path_separator = :
# path_separator = ;
# path_separator = space
# path_separator = newline
#
# Use os.pathsep. Default configuration used for new projects.
path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

# database URL.  This is consumed by the user-maintained env.py script only.
# other means of configuring database URLs may be customized within the env.py
# file.
sqlalchemy.url = driver://user:pass@localhost/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the module runner, against the "ruff" module
# hooks = ruff
# ruff.type = module
# ruff.module = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Alternatively, use the exec runner to execute a binary found on your PATH
# hooks = ruff
# ruff.type = exec
# ruff.executable = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Logging configuration.  This is also consumed by the user-maintained
# env.py script only.
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```


### `app/__init__.py`

```python
def main() -> None:
    print("Hello from app!")
```


### `app/base_datos.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

URL_BASE_DATOS = os.getenv("DATABASE_URL", "sqlite:///./minimarket.db")

if URL_BASE_DATOS.startswith("sqlite"):
    motor = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
else:
    motor = create_engine(URL_BASE_DATOS)


SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()

def obtener_bd():
    bd = SesionLocal()
    try:
        yield bd
    finally:
        bd.close()
```


### `app/domain/categorias.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid
    
@dataclass
class Categoria:
    nombre_categoria: str
    descripcion : str
    activa : bool 
    fecha_creacion : datetime = field(default_factory=datetime.now)
    fecha_actualizacion : datetime = field(default_factory=datetime.now)
    id_categoria : str = field(default_factory=lambda: str(uuid.uuid4()))
```


### `app/domain/detalleventa.py`

```python
from dataclasses import dataclass, field
import uuid

@dataclass
class DetalleVenta:
    id_producto: str
    id_venta: str
    cantidad_producto:  int
    subtotal: int
    precio_unitario: int
    iva: float
    descuento: float
    id_detalle:  str = field(default_factory=lambda: str(uuid.uuid4()))
```


### `app/domain/pago.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from datetime import date
import uuid


class EstadoPago(str, Enum):
    PENDIENTE = "pendiente"
    EXITOSO = "exitoso"
    RECHAZADO = "rechazado"

@dataclass
class Pago:
    id_venta: str 
    fecha_pago: date
    monto: float
    metodo_pago: str
    estado_pago: EstadoPago 
    id_pago: str = field(default_factory=lambda: str(uuid.uuid4()))
```


### `app/domain/productos.py`

```python
from dataclasses import dataclass, field
from datetime import datetime 
import uuid

@dataclass
class Producto:
    nombre_producto: str
    descripcion: str
    stock: int
    stock_minimo : int
    id_categoria: str
    precio: int
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    id_producto: str = field(default_factory=lambda: str(uuid.uuid4()))
```


### `app/domain/venta.py`

```python
from dataclasses import dataclass, field
from datetime import date
import uuid

from app.domain.detalleventa import DetalleVenta

@dataclass
class Venta:
    cliente: str
    fecha_venta: date
    total: float = 0.0
    id_venta: str = field(default_factory=lambda: str(uuid.uuid4()))
    detalles: list[DetalleVenta] = field(default_factory=list)
```


### `app/excepciones.py`

```python
class ApiError(Exception):
    def __init__(self, message: str, details: list[str] | None = None):
        self.message = message
        self.details = details or []
        super().__init__(message)


class ResourceNotFoundError(ApiError):
    code = "RESOURCE_NOT_FOUND"
    status_code = 404


class ConflictError(ApiError):
    code = "CONFLICT"
    status_code = 409


class BusinessRuleError(ApiError):
    code = "BUSINESS_RULE_VIOLATION"
    status_code = 400
```


### `app/main.py`

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .excepciones import ApiError
from .routers import categorias_routers, productos_routers, venta_router
from .routers.pago_ruta import router as pago_router
from .routers.detalle_venta_ruta import router as detalle_venta_router
from .schemas.common import ErrorDetail, ErrorResponse


app = FastAPI()

def _envelope(code: str, message: str, details: list[str]) -> dict:
    return ErrorResponse(error=ErrorDetail(code=code, message=message, details=details)).model_dump()


@app.exception_handler(ApiError)
async def controlar_api_error(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def controlar_validation_error(request: Request, exc: RequestValidationError):
    detalles = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content=_envelope("VALIDATION_ERROR", "Los datos no cumplen las validaciones del esquema", detalles),
    )


@app.exception_handler(StarletteHTTPException)
async def controlar_http_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope("HTTP_ERROR", str(exc.detail), []),
    )

app.include_router(venta_router.router)
app.include_router(categorias_routers.router)
app.include_router(productos_routers.router)
app.include_router(detalle_venta_router)
app.include_router(pago_router)

from .models import categoria_modelos, pago_modelos, producto_modelos, venta_modelos
```


### `app/models/__init__.py`

```python

```


### `app/models/categoria_modelos.py`

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.base_datos import Base


class CategoriaBD(Base):
    __tablename__ = "categorias"

    id_categoria = Column(String, primary_key=True, index=True)
    nombre_categoria = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=False)
    activa = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)

    productos = relationship("ProductoBD", back_populates="categoria")
```


### `app/models/detalle_venta_modelos.py`

```python
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos import Base

class DetalleVentaBD(Base):
    __tablename__ = "detalles_ventas"

    id_detalle = Column(String, primary_key=True, index=True)
    id_producto = Column(String, ForeignKey("productos.id_producto"), nullable=False)
    id_venta = Column(String, ForeignKey("ventas.id_venta"), nullable=False)
    cantidad_producto = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    iva = Column(Float, nullable=False, default=0.19)
    descuento = Column(Float, nullable=False, default=0.0)

    venta = relationship("VentaBD", back_populates="detalles")
```


### `app/models/pago_modelos.py`

```python
from sqlalchemy import Column, Date, Float, ForeignKey, String
from app.base_datos import Base


class PagoBD(Base):
    __tablename__ = "pagos"

    id_pago = Column(String, primary_key=True, index=True)
    id_venta = Column(
        String,
        ForeignKey("ventas.id_venta"),
        nullable=False,
        index=True,
    )
    fecha_pago = Column(Date, nullable=False)
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(30), nullable=False)
    estado_pago = Column(String(20), nullable=False)
```


### `app/models/producto_modelos.py`

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos import Base

class ProductoBD(Base):
    __tablename__ = "productos"

    id_producto = Column(String, primary_key=True, index=True)
    nombre_producto = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=False)
    stock = Column(Integer, nullable=False)
    stock_minimo = Column(Integer, nullable=False)
    id_categoria = Column(String, ForeignKey("categorias.id_categoria"), nullable=False)
    precio = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    
    categoria = relationship("CategoriaBD", back_populates="productos")
```


### `app/models/venta_modelos.py`

```python
from sqlalchemy import Column, String, Float, Date
from sqlalchemy.orm import relationship
from app.base_datos import Base

class VentaBD(Base):
    __tablename__ = "ventas"

    id_venta = Column(String, primary_key=True, index=True)
    cliente = Column(String(90), nullable=False)
    fecha_venta = Column(Date, nullable=False)
    total = Column(Float, default=0.0)
    detalles = relationship(
        "DetalleVentaBD",
        back_populates="venta",
        cascade="all, delete-orphan",
        )
```


### `app/repositories/categorias_repositorio.py`

```python
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..excepciones import ConflictError, ResourceNotFoundError
from ..domain.categorias import Categoria
from ..models.categoria_modelos import CategoriaBD


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
        bd.delete(categoria)
        bd.commit()

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
```


### `app/repositories/detalle_venta_repositorio.py`

```python
from app.domain.detalleventa import DetalleVenta
from typing import List
from sqlalchemy.orm import Session
from app.excepciones import ResourceNotFoundError
from app.models.detalle_venta_modelos import DetalleVentaBD

class DetalleVentaRepositorio:
    def obtener_todos_de_una_venta(
        self,
        bd: Session,
        id_venta: str,
    ) -> List[DetalleVenta]:
        detalles_bd = (
            bd.query(DetalleVentaBD)
            .filter(DetalleVentaBD.id_venta == id_venta)
            .all()
        )

        return [self._a_entidad(detalle) for detalle in detalles_bd]
    
    def obtener_por_id(
        self,
        bd: Session,
        id_venta: str,
        id_detalle: str,
    ) -> DetalleVenta:
        detalle_bd = (
            bd.query(DetalleVentaBD)
            .filter(
                DetalleVentaBD.id_venta == id_venta,
                DetalleVentaBD.id_detalle == id_detalle,
            )
            .first()
        )

        if detalle_bd is None:
            raise ResourceNotFoundError(
                f"El detalle {id_detalle} no existe en la venta {id_venta}"
            )

        return self._a_entidad(detalle_bd)

    def _a_entidad(self, detalle_bd: DetalleVentaBD) -> DetalleVenta:
        return DetalleVenta(
            id_detalle=detalle_bd.id_detalle,
            id_producto=detalle_bd.id_producto,
            id_venta=detalle_bd.id_venta,
            cantidad_producto=detalle_bd.cantidad_producto,
            subtotal=detalle_bd.subtotal,
            precio_unitario=detalle_bd.precio_unitario,
            iva=detalle_bd.iva,
            descuento=detalle_bd.descuento,
        )

detalle_venta_repositorio = DetalleVentaRepositorio()
```


### `app/repositories/pago_repositorio.py`

```python
from sqlalchemy.orm import Session

from app.domain.pago import EstadoPago, Pago
from app.models.pago_modelos import PagoBD


class PagoRepositorio:
    def guardar(self, bd: Session, pago: Pago) -> Pago:
        pago_bd = PagoBD(
            id_pago=pago.id_pago,
            id_venta=pago.id_venta,
            fecha_pago=pago.fecha_pago,
            monto=pago.monto,
            metodo_pago=pago.metodo_pago,
            estado_pago=pago.estado_pago.value,
        )
        bd.add(pago_bd)
        bd.commit()
        bd.refresh(pago_bd)
        return self._a_entidad(pago_bd)

    def obtener_por_id(self, bd: Session, id_pago: str) -> Pago | None:
        pago_bd = (
            bd.query(PagoBD)
            .filter(PagoBD.id_pago == id_pago)
            .first()
        )
        return self._a_entidad(pago_bd) if pago_bd else None

    def listar(self, bd: Session) -> list[Pago]:
        pagos_bd = bd.query(PagoBD).all()
        return [self._a_entidad(pago_bd) for pago_bd in pagos_bd]

    def obtener_por_venta(self, bd: Session, id_venta: str) -> list[Pago]:
        pagos_bd = (
            bd.query(PagoBD)
            .filter(PagoBD.id_venta == id_venta)
            .all()
        )
        return [self._a_entidad(pago_bd) for pago_bd in pagos_bd]

    def existe_pago_exitoso(self, bd: Session, id_venta: str) -> bool:
        return (
            bd.query(PagoBD)
            .filter(
                PagoBD.id_venta == id_venta,
                PagoBD.estado_pago == EstadoPago.EXITOSO.value,
            )
            .first()
            is not None
        )

    @staticmethod
    def _a_entidad(pago_bd: PagoBD) -> Pago:
        return Pago(
            id_pago=pago_bd.id_pago,
            id_venta=pago_bd.id_venta,
            fecha_pago=pago_bd.fecha_pago,
            monto=pago_bd.monto,
            metodo_pago=pago_bd.metodo_pago,
            estado_pago=EstadoPago(pago_bd.estado_pago),
        )


pago_repositorio = PagoRepositorio()
```


### `app/repositories/productos_repositorio.py`

```python
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..excepciones import ConflictError, ResourceNotFoundError
from ..domain.productos import Producto
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

    def actualizar(self, bd: Session, id_producto: str, entidad: Producto) -> Producto:
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
        bd.commit()
        return entidad

    def eliminar(self, bd: Session, id_producto: str) -> None:
        producto = bd.query(ProductoBD).filter(ProductoBD.id_producto == id_producto).first()
        if producto is None:
            raise ResourceNotFoundError("No existe un producto con el ID solicitado")
        bd.delete(producto)
        bd.commit()

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
```


### `app/repositories/seeder/__init__.py`

```python
"""Seeders reproducibles para datos de demostración."""
```


### `app/repositories/seeder/seed_categorias.py`

```python
import uuid

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.categoria_modelos import CategoriaBD


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
```


### `app/repositories/seeder/seed_detalles_ventas.py`

```python
from sqlalchemy.orm import Session

from app.models.detalle_venta_modelos import DetalleVentaBD
from app.models.producto_modelos import ProductoBD
from app.models.venta_modelos import VentaBD


DETALLES = [
    ("demo-detalle-001", "demo-venta-001", "demo-arroz", 2),
    ("demo-detalle-002", "demo-venta-001", "demo-jugo", 1),
    ("demo-detalle-003", "demo-venta-002", "demo-arroz", 1),
    ("demo-detalle-004", "demo-venta-002", "demo-jugo", 1),
]


def seedear_detalles_ventas(bd: Session) -> int:
    ventas = {venta.id_venta: venta for venta in bd.query(VentaBD).all()}
    productos = {producto.id_producto: producto for producto in bd.query(ProductoBD).all()}
    ids_faltantes_venta = sorted({fila[1] for fila in DETALLES if fila[1] not in ventas})
    ids_faltantes_producto = sorted({fila[2] for fila in DETALLES if fila[2] not in productos})
    if ids_faltantes_venta or ids_faltantes_producto:
        raise ValueError(
            "Primero ejecuta los seeders de ventas y productos. "
            f"Ventas faltantes: {ids_faltantes_venta}; productos faltantes: {ids_faltantes_producto}"
        )

    existentes = {id_detalle for (id_detalle,) in bd.query(DetalleVentaBD.id_detalle).all()}
    nuevos = []
    for id_detalle, id_venta, id_producto, cantidad in DETALLES:
        if id_detalle in existentes:
            continue
        producto = productos[id_producto]
        nuevos.append(
            DetalleVentaBD(
                id_detalle=id_detalle,
                id_venta=id_venta,
                id_producto=id_producto,
                cantidad_producto=cantidad,
                precio_unitario=producto.precio,
                subtotal=cantidad * producto.precio,
                iva=0.0,
                descuento=0.0,
            )
        )
    bd.add_all(nuevos)
    bd.flush()
    return len(nuevos)
```


### `app/repositories/seeder/seed_pagos.py`

```python
from datetime import date

from sqlalchemy.orm import Session

from app.models.pago_modelos import PagoBD
from app.models.venta_modelos import VentaBD


PAGOS = [
    ("demo-pago-001", "demo-venta-001", date(2026, 10, 1), 4600.0, "debito", "exitoso"),
    ("demo-pago-002", "demo-venta-002", date(2026, 10, 2), 3400.0, "credito", "exitoso"),
]


def seedear_pagos(bd: Session) -> int:
    ventas = {venta.id_venta: venta for venta in bd.query(VentaBD).all()}
    faltantes = sorted({fila[1] for fila in PAGOS if fila[1] not in ventas})
    if faltantes:
        raise ValueError(f"Primero ejecuta el seeder de ventas. Ventas faltantes: {faltantes}")

    existentes = {id_pago for (id_pago,) in bd.query(PagoBD.id_pago).all()}
    nuevos = [
        PagoBD(
            id_pago=id_pago,
            id_venta=id_venta,
            fecha_pago=fecha,
            monto=monto,
            metodo_pago=metodo,
            estado_pago=estado,
        )
        for id_pago, id_venta, fecha, monto, metodo, estado in PAGOS
        if id_pago not in existentes
    ]
    bd.add_all(nuevos)
    bd.flush()
    return len(nuevos)
```


### `app/repositories/seeder/seed_productos.py`

```python
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.categoria_modelos import CategoriaBD
from app.models.producto_modelos import ProductoBD


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
```


### `app/repositories/seeder/seed_todos.py`

```python
"""Carga datos demo en orden de dependencias. Ejecutar desde la raíz:
python -m app.repositories.seeder.seed_todos
"""

from app.base_datos import Base, SesionLocal, motor
from app.models import categoria_modelos, detalle_venta_modelos, pago_modelos, producto_modelos, venta_modelos
from app.repositories.seeder.seed_categorias import seedear_categorias
from app.repositories.seeder.seed_detalles_ventas import seedear_detalles_ventas
from app.repositories.seeder.seed_pagos import seedear_pagos
from app.repositories.seeder.seed_productos import seedear_productos
from app.repositories.seeder.seed_ventas import seedear_ventas


def seedear_todo() -> dict[str, int]:
    Base.metadata.create_all(bind=motor)
    bd = SesionLocal()
    try:
        resultados = {
            "categorias": seedear_categorias(bd),
            "productos": seedear_productos(bd),
            "ventas": seedear_ventas(bd),
            "detalles_ventas": seedear_detalles_ventas(bd),
            "pagos": seedear_pagos(bd),
        }
        bd.commit()
        return resultados
    except Exception:
        bd.rollback()
        raise
    finally:
        bd.close()


if __name__ == "__main__":
    insertados = seedear_todo()
    print("Registros nuevos insertados:")
    for entidad, cantidad in insertados.items():
        print(f"- {entidad}: {cantidad}")
```


### `app/repositories/seeder/seed_ventas.py`

```python
from datetime import date

from sqlalchemy.orm import Session

from app.models.venta_modelos import VentaBD


VENTAS = [
    ("demo-venta-001", "Cliente Demo Uno", date(2026, 10, 1), 4600.0),
    ("demo-venta-002", "Cliente Demo Dos", date(2026, 10, 2), 3400.0),
]


def seedear_ventas(bd: Session) -> int:
    existentes = {id_venta for (id_venta,) in bd.query(VentaBD.id_venta).all()}
    nuevas = [
        VentaBD(
            id_venta=id_venta,
            cliente=cliente,
            fecha_venta=fecha,
            total=total,
        )
        for id_venta, cliente, fecha, total in VENTAS
        if id_venta not in existentes
    ]
    bd.add_all(nuevas)
    bd.flush()
    return len(nuevas)
```


### `app/repositories/venta_repositorio.py`

```python
from sqlalchemy.orm import Session
from app.domain.venta import Venta
from app.domain.detalleventa import DetalleVenta
from app.excepciones import ResourceNotFoundError
from app.models.venta_modelos import VentaBD
from app.models.detalle_venta_modelos import DetalleVentaBD

class VentaRepositorio:
    def crear_venta(self, bd: Session, venta: Venta) -> Venta:
        venta_bd = VentaBD(
            id_venta=venta.id_venta,
            cliente=venta.cliente,
            fecha_venta=venta.fecha_venta,
            total=venta.total
        )

        for d in venta.detalles:
            detalle_bd = DetalleVentaBD(
                id_detalle=d.id_detalle,
                id_producto=d.id_producto,
                id_venta=venta.id_venta,
                cantidad_producto=d.cantidad_producto,
                precio_unitario=d.precio_unitario,
                subtotal=d.subtotal,
                iva=getattr(d, "iva", 0.0),
                descuento=getattr(d, "descuento", 0.0)
            )
            venta_bd.detalles.append(detalle_bd)

        bd.add(venta_bd)
        bd.commit()
        bd.refresh(venta_bd)
        return venta

    def obtener_por_id(self, bd: Session, id_venta: str) -> Venta:
        venta_bd = bd.query(VentaBD).filter(VentaBD.id_venta == id_venta).first()
        if not venta_bd:
            raise ResourceNotFoundError(f"No existe una venta con el ID {id_venta}")

        detalles_bd = []
        if hasattr(venta_bd, "detalles") and venta_bd.detalles:
            for d in venta_bd.detalles:
                detalles_bd.append(
                    DetalleVenta(
                        id_detalle=d.id_detalle,
                        id_producto=d.id_producto,
                        id_venta=d.id_venta,
                        cantidad_producto=d.cantidad_producto,
                        precio_unitario=d.precio_unitario,
                        subtotal=d.subtotal,
                        iva=getattr(d, "iva", 0.0),
                        descuento=getattr(d, "descuento", 0.0)
                    )
                )

            return Venta(
                id_venta=venta_bd.id_venta,
                cliente=venta_bd.cliente,
                fecha_venta=venta_bd.fecha_venta,
                total=venta_bd.total,
                detalles=detalles_bd
            )

    def listar_todas(self, bd: Session) -> list[Venta]:
        ventas_bd = bd.query(VentaBD).all()
        return [self.obtener_por_id(bd, v.id_venta) for v in ventas_bd]

    def eliminar_venta(self, bd: Session, id_venta: str):
        venta_bd = bd.query(VentaBD).filter(VentaBD.id_venta == id_venta).first()
        if not venta_bd:
            raise ResourceNotFoundError(f"No existe una venta con el ID {id_venta}")
        bd.delete(venta_bd)
        bd.commit()

venta_repositorio = VentaRepositorio()
```


### `app/routers/categorias_routers.py`

```python
from typing import Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..base_datos import obtener_bd
from ..schemas.categorias_schemas import CategoriaCreate, CategoriaPatch, CategoriaResponse
from ..domain.categorias import Categoria
from ..schemas.common import PaginatedResponse
from ..services.categorias_service import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate, bd: Session = Depends(obtener_bd)) -> Categoria:
    return categoria_service.crear(bd, categoria)


@router.get("/", response_model=PaginatedResponse[CategoriaResponse])
def obtener_categorias(activa: bool | None = None,
                       nombre: str | None = None,
                       ordenar_por: str = Query("nombre_categoria"),
                       direccion: Literal["asc", "desc"] = "asc",
                       pagina: int = Query(1, ge=1),
                       limite: int = Query(20, ge=1, le=100),
                       bd: Session = Depends(obtener_bd)) -> PaginatedResponse[CategoriaResponse]:
    return categoria_service.obtener_categorias(bd, activa=activa, nombre=nombre, ordenar_por=ordenar_por,
                                                direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria_por_id(id_categoria: str, bd: Session = Depends(obtener_bd)) -> CategoriaResponse:
    return categoria_service.obtener_por_id(bd, id_categoria)


@router.patch("/{id_categoria}", response_model=CategoriaResponse)
def actualizar_categoria(id_categoria: str, datos: CategoriaPatch, bd: Session = Depends(obtener_bd)) -> CategoriaResponse:
    return categoria_service.actualizar(bd, id_categoria, datos)


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: str, bd: Session = Depends(obtener_bd)) -> None:
    categoria_service.eliminar(bd, id_categoria)
```


### `app/routers/detalle_venta_ruta.py`

```python
from fastapi import APIRouter, Depends
from typing import List
from app.domain.detalleventa import DetalleVenta
from app.services.detalle_venta_servicio import DetalleVentaServicio
from sqlalchemy.orm import Session
from app.base_datos import obtener_bd

router = APIRouter(prefix="/ventas", tags=["Detalles de Venta"])
service = DetalleVentaServicio()


@router.get("/{id_venta}/detalles", response_model=List[DetalleVenta])
def listar_detalles(
    id_venta: str,
    bd: Session = Depends(obtener_bd),                
):
    return service.obtener_detalles_por_venta(bd, id_venta)

@router.get("/{id_venta}/detalles/{id_detalle}", response_model=DetalleVenta)
def obtener_detalle(
    id_venta: str, 
    id_detalle: str,
    bd: Session = Depends(obtener_bd),
):
    return service.obtener_detalle_especifico(bd, id_venta, id_detalle)
```


### `app/routers/pago_ruta.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.base_datos import obtener_bd
from app.schemas.pago_schemas import CrearPago, PagoRespuesta
from app.services.pago_servicio import (
    listar_pagos,
    obtener_pago,
    procesar_pago,
)


router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post("", response_model=PagoRespuesta, status_code=201,
             summary="procesar el pago de una venta")
def post_pago(datos: CrearPago, bd: Session = Depends(obtener_bd)):
    return procesar_pago(bd, datos)


@router.get("", response_model=list[PagoRespuesta],
            summary="listar todos los pagos registrados")
def get_pagos(bd: Session = Depends(obtener_bd)):
    return listar_pagos(bd)


@router.get("/{id_pago}", response_model=PagoRespuesta,
            summary="obtener un pago por su ID")
def get_pago(id_pago: str, bd: Session = Depends(obtener_bd)):
    return obtener_pago(bd, id_pago)
```


### `app/routers/productos_routers.py`

```python
from typing import Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..base_datos import obtener_bd
from ..schemas.productos_schemas import ProductoCreate, ProductoPatch, ProductoResponse
from ..domain.productos import Producto
from ..schemas.common import PaginatedResponse
from ..services.productos_service import producto_service

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate, bd: Session = Depends(obtener_bd)) -> Producto:
    return producto_service.crear(bd, datos)


@router.get("/", response_model=PaginatedResponse[ProductoResponse])
def obtener_productos(id_categoria: str | None = None,
                      nombre: str | None = None,
                      ordenar_por: str = Query("nombre_producto"),
                      direccion: Literal["asc", "desc"] = "asc",
                      pagina: int = Query(1, ge=1),
                      limite: int = Query(20, ge=1, le=100),
                      bd: Session = Depends(obtener_bd)) -> PaginatedResponse[ProductoResponse]:
    return producto_service.obtener_productos(bd, id_categoria=id_categoria, nombre=nombre, ordenar_por=ordenar_por,
                                              direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_producto}", response_model=ProductoResponse)
def obtener_producto_por_id(id_producto: str, bd: Session = Depends(obtener_bd)) -> ProductoResponse:
    return producto_service.obtener_por_id(bd, id_producto)


@router.patch("/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(id_producto: str, datos: ProductoPatch, bd: Session = Depends(obtener_bd)) -> ProductoResponse:
    return producto_service.actualizar(bd, id_producto, datos)


@router.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id_producto: str, bd: Session = Depends(obtener_bd)) -> None:
    producto_service.eliminar(bd, id_producto)
```


### `app/routers/venta_router.py`

```python
from typing import Literal, Optional
from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.orm import Session

from app.schemas.venta_esquemas import VentaCreada, VentaRespuesta
from app.schemas.common import PaginatedResponse
from app.services.venta_servicio import venta_servicio
from app.base_datos import obtener_bd

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("", response_model=VentaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_venta_endpoint(datos: VentaCreada, bd: Session = Depends(obtener_bd)):
    venta = venta_servicio.crear_venta(bd, datos)
    return venta

@router.get("", response_model= PaginatedResponse[VentaRespuesta])
def obtener_ventas(cliente: str = None,
    ordenar_por: Optional[Literal["cliente", "total", "fecha_venta"]] = None,
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    bd: Session = Depends(obtener_bd)
):
    return venta_servicio.listar_venta(bd, cliente, ordenar_por, direccion, pagina, limite)

@router.get("/{id_venta}", response_model=VentaRespuesta)
def obtener_venta_por_id(id_venta: str, bd: Session = Depends(obtener_bd)):
    return venta_servicio.obtener_venta(bd, id_venta)

@router.get("/{id_venta}/boleta")
def obtener_boleta(id_venta: str, bd: Session = Depends(obtener_bd)):
    return venta_servicio.generar_boleta(bd, id_venta)

@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_venta_endpoint(id_venta: str, bd: Session = Depends(obtener_bd)):
    venta_servicio.eliminar_venta(bd, id_venta)
```


### `app/schemas/categorias_schemas.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CategoriaCreate(BaseModel):
    nombre_categoria: str = Field(max_length=50)
    descripcion: str = Field(max_length=255)
    activa: bool

class CategoriaPatch(BaseModel):
    nombre_categoria: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activa: Optional[bool] = None

class CategoriaResponse(BaseModel):
    id_categoria: str
    nombre_categoria: str
    descripcion: str
    activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    cantidad_productos: int
```


### `app/schemas/common.py`

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[str] = []


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    pagina: int
    limite: int
    total_paginas: int
```


### `app/schemas/detalle_venta_esquema.py`

```python
from pydantic import BaseModel

class DetalleVentaCrear(BaseModel):
    id_producto: str
    cantidad_producto: int

class DetalleVentaRespuesta(BaseModel):
    id_detalle: str
    id_producto: str
    cantidad_producto: int
    precio_unitario: int
    subtotal: int
    iva: float
    descuento: float

    class Config:
        from_attributes = True
```


### `app/schemas/pago_schemas.py`

```python
from pydantic import BaseModel, Field
from datetime import date
from app.domain.pago import EstadoPago

#DTO entrada
class CrearPago(BaseModel):
    id_venta: str
    monto: float = Field(gt=0, description="debe ser mayor a 0")
    metodo_pago: str = Field(min_length=3, max_length=30)

#DTO salida 
class PagoRespuesta(BaseModel):
    id_pago: str
    id_venta: str
    fecha_pago: date
    monto: float
    metodo_pago: str
    estado_pago: EstadoPago
```


### `app/schemas/productos_schemas.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ProductoCreate(BaseModel):
    nombre_producto: str = Field(max_length=50)
    descripcion: str = Field(max_length=255)
    stock: int
    stock_minimo: int
    id_categoria: str
    precio: int

class ProductoPatch(BaseModel):
    nombre_producto: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    id_categoria: Optional[str] = None
    precio: Optional[int] = None

class ProductoResponse(BaseModel):
    id_producto: str
    nombre_producto: str
    descripcion: str
    stock: int
    stock_minimo: int
    id_categoria: str
    precio: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
```


### `app/schemas/venta_esquemas.py`

```python
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.detalle_venta_esquema import DetalleVentaCrear, DetalleVentaRespuesta
from app.schemas.pago_schemas import PagoRespuesta

class VentaCreada(BaseModel):
    cliente: str = Field(..., min_length=3, max_length=90)
    detalles: list[DetalleVentaCrear] = Field(..., min_length=1)

class VentaRespuesta(BaseModel):
    id_venta: str
    fecha_venta: date
    cliente: str
    total: float
    detalles: list[DetalleVentaRespuesta]
    pago: Optional[PagoRespuesta] = None
```


### `app/services/categorias_service.py`

```python
from datetime import datetime
import math
from sqlalchemy.orm import Session
from ..excepciones import BusinessRuleError
from ..domain.categorias import Categoria
from ..schemas.categorias_schemas import CategoriaCreate, CategoriaPatch, CategoriaResponse
from ..schemas.common import PaginatedResponse
from ..repositories.categorias_repositorio import categoria_repositorio
from ..repositories.productos_repositorio import producto_repositorio

CAMPOS_ORDEN = {"nombre_categoria", "descripcion", "activa", "fecha_creacion", "fecha_actualizacion"}


class CategoriaService:
    def _a_categoria_response(self, bd: Session, categoria: Categoria) -> CategoriaResponse:
        return CategoriaResponse(
            id_categoria=categoria.id_categoria,
            nombre_categoria=categoria.nombre_categoria,
            descripcion=categoria.descripcion,
            activa=categoria.activa,
            fecha_creacion=categoria.fecha_creacion,
            fecha_actualizacion=categoria.fecha_actualizacion,
            cantidad_productos=producto_repositorio.contar_por_categoria(bd, categoria.id_categoria),
        )

    def crear(self, bd: Session, categoria: CategoriaCreate) -> Categoria:
        entidad = Categoria(**categoria.model_dump())
        return categoria_repositorio.crear(bd, entidad)

    def obtener_categorias( self,
                            bd: Session,
                            activa: bool | None = None,
                            nombre: str | None = None,
                            ordenar_por: str = "nombre_categoria",
                            direccion: str = "asc",
                            pagina: int = 1,
                            limite: int = 20) -> PaginatedResponse[CategoriaResponse]:
        if ordenar_por not in CAMPOS_ORDEN:
            raise BusinessRuleError(f"El campo '{ordenar_por}' no es válido para ordenar")

        filtradas = categoria_repositorio.obtener_todas(bd)
        if activa is not None:
            filtradas = [c for c in filtradas if c.activa == activa]
        if nombre:
            filtradas = [c for c in filtradas if nombre.lower() in c.nombre_categoria.lower()]

        reverse = direccion == "desc"
        filtradas = sorted(filtradas, key=lambda c: getattr(c, ordenar_por), reverse=reverse)

        total = len(filtradas)
        total_paginas = math.ceil(total / limite) if total > 0 else 0
        inicio = (pagina - 1) * limite
        items = [self._a_categoria_response(bd, c) for c in filtradas[inicio:inicio + limite]]

        return PaginatedResponse(items=items, total=total, pagina=pagina,
                                 limite=limite, total_paginas=total_paginas)

    def obtener_por_id(self, bd: Session, id_categoria: str) -> CategoriaResponse:
        return self._a_categoria_response(bd, categoria_repositorio.obtener_por_id(bd, id_categoria))

    def actualizar(self, bd: Session, id_categoria: str, datos: CategoriaPatch) -> CategoriaResponse:
        entidad = categoria_repositorio.obtener_por_id(bd, id_categoria)
        if datos.nombre_categoria is not None:
            entidad.nombre_categoria = datos.nombre_categoria
        if datos.descripcion is not None:
            entidad.descripcion = datos.descripcion
        if datos.activa is not None:
            entidad.activa = datos.activa
        entidad.fecha_actualizacion = datetime.now()
        categoria_repositorio.actualizar(bd, id_categoria, entidad)
        return self._a_categoria_response(bd, entidad)

    def eliminar(self, bd: Session, id_categoria: str) -> None:
        return categoria_repositorio.eliminar(bd, id_categoria)


categoria_service = CategoriaService()
```


### `app/services/detalle_venta_servicio.py`

```python
from typing import List
from app.domain.detalleventa import DetalleVenta
from sqlalchemy.orm import Session
from app.repositories.detalle_venta_repositorio import detalle_venta_repositorio

class DetalleVentaServicio:
    def obtener_detalles_por_venta(
        self,
        bd: Session,
        id_venta: str,
    ) -> List[DetalleVenta]:
        return detalle_venta_repositorio.obtener_todos_de_una_venta(bd, id_venta)

    def obtener_detalle_especifico(
        self,
        bd: Session,
        id_venta: str,
        id_detalle: str,
    ) -> DetalleVenta:
        return detalle_venta_repositorio.obtener_por_id(bd, id_venta, id_detalle)
```


### `app/services/pago_servicio.py`

```python
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.domain.pago import EstadoPago, Pago
from app.excepciones import BusinessRuleError, ResourceNotFoundError
from app.repositories.pago_repositorio import pago_repositorio
from app.repositories.venta_repositorio import venta_repositorio
from app.schemas.pago_schemas import CrearPago


def procesar_pago(bd: Session, datos: CrearPago) -> Pago:
    venta = venta_repositorio.obtener_por_id(bd, datos.id_venta)

    if pago_repositorio.existe_pago_exitoso(bd, datos.id_venta):
        raise BusinessRuleError("La venta ya se encuentra pagada")

    if round(datos.monto, 2) != round(venta.total, 2):
        raise BusinessRuleError(
            f"El monto debe ser igual al total de la venta ({venta.total})"
        )

    nuevo_pago = Pago(
        id_pago=str(uuid.uuid4()),
        id_venta=datos.id_venta,
        fecha_pago=date.today(),
        monto=datos.monto,
        metodo_pago=datos.metodo_pago,
        estado_pago=EstadoPago.EXITOSO,
    )
    return pago_repositorio.guardar(bd, nuevo_pago)


def obtener_pago(bd: Session, id_pago: str) -> Pago:
    pago = pago_repositorio.obtener_por_id(bd, id_pago)
    if pago is None:
        raise ResourceNotFoundError(f"No existe un pago con el ID {id_pago}")
    return pago


def listar_pagos(bd: Session) -> list[Pago]:
    return pago_repositorio.listar(bd)
```


### `app/services/productos_service.py`

```python
from datetime import datetime
import math
from sqlalchemy.orm import Session
from ..excepciones import BusinessRuleError
from ..domain.productos import Producto
from ..schemas.productos_schemas import ProductoCreate, ProductoPatch, ProductoResponse
from ..schemas.common import PaginatedResponse
from ..repositories.categorias_repositorio import categoria_repositorio
from ..repositories.productos_repositorio import producto_repositorio

CAMPOS_ORDEN = {"nombre_producto", "descripcion", "stock", "stock_minimo",
                "id_categoria", "precio", "fecha_creacion", "fecha_actualizacion"}


class ProductoService:
    def _a_producto_response(self, producto: Producto) -> ProductoResponse:
        return ProductoResponse(
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

    def crear(self, bd: Session, datos: ProductoCreate) -> Producto:
        categoria_repositorio.obtener_por_id(bd, datos.id_categoria)
        entidad = Producto(**datos.model_dump())
        return producto_repositorio.crear(bd, entidad)

    def obtener_productos(self,
                          bd: Session,
                          id_categoria: str | None = None,
                          nombre: str | None = None,
                          ordenar_por: str = "nombre_producto",
                          direccion: str = "asc",
                          pagina: int = 1,
                          limite: int = 20) -> PaginatedResponse[ProductoResponse]:
        if ordenar_por not in CAMPOS_ORDEN:
            raise BusinessRuleError(f"El campo '{ordenar_por}' no es válido para ordenar")

        filtrados = producto_repositorio.obtener_todos(bd)
        if id_categoria is not None:
            filtrados = [p for p in filtrados if p.id_categoria == id_categoria]
        if nombre:
            filtrados = [p for p in filtrados if nombre.lower() in p.nombre_producto.lower()]

        reverse = direccion == "desc"
        filtrados = sorted(filtrados, key=lambda p: getattr(p, ordenar_por), reverse=reverse)

        total = len(filtrados)
        total_paginas = math.ceil(total / limite) if total > 0 else 0
        inicio = (pagina - 1) * limite
        items = [self._a_producto_response(p) for p in filtrados[inicio:inicio + limite]]

        return PaginatedResponse(items=items, total=total, pagina=pagina,
                                 limite=limite, total_paginas=total_paginas)

    def obtener_por_id(self, bd: Session, id_producto: str) -> ProductoResponse:
        return self._a_producto_response(producto_repositorio.obtener_por_id(bd, id_producto))

    def actualizar(self, bd: Session, id_producto: str, datos: ProductoPatch) -> ProductoResponse:
        entidad = producto_repositorio.obtener_por_id(bd, id_producto)
        if datos.nombre_producto is not None:
            entidad.nombre_producto = datos.nombre_producto
        if datos.descripcion is not None:
            entidad.descripcion = datos.descripcion
        if datos.stock is not None:
            entidad.stock = datos.stock
        if datos.stock_minimo is not None:
            entidad.stock_minimo = datos.stock_minimo
        if datos.id_categoria is not None:
            categoria_repositorio.obtener_por_id(bd, datos.id_categoria)
            entidad.id_categoria = datos.id_categoria
        if datos.precio is not None:
            entidad.precio = datos.precio
        entidad.fecha_actualizacion = datetime.now()
        return self._a_producto_response(producto_repositorio.actualizar(bd, id_producto, entidad))

    def eliminar(self, bd: Session, id_producto: str) -> None:
        return producto_repositorio.eliminar(bd, id_producto)


producto_service = ProductoService()
```


### `app/services/venta_servicio.py`

```python
import math
from datetime import date
from sqlalchemy.orm import Session

from app.domain.venta import Venta
from app.domain.detalleventa import DetalleVenta
from app.schemas.venta_esquemas import VentaCreada, VentaRespuesta
from app.excepciones import BusinessRuleError, ConflictError, ResourceNotFoundError
from app.schemas.common import PaginatedResponse
from app.schemas.pago_schemas import PagoRespuesta
from app.schemas.detalle_venta_esquema import DetalleVentaRespuesta

from app.repositories.productos_repositorio import producto_repositorio
from app.repositories.venta_repositorio import venta_repositorio
from app.repositories.pago_repositorio import pago_repositorio

class VentaServicio:
    def __init__(self):
        self.CAMPOS_ORDEN = {"cliente", "total", "fecha_venta"}

    def calcular_total(self, venta: Venta):
        total = 0.0
        for detalle in venta.detalles:
            total = total + detalle.subtotal
        venta.total = total
        return total

    def a_venta_out(self,bd:Session, venta: Venta) -> VentaRespuesta:
        pagos = pago_repositorio.obtener_por_venta(bd, venta.id_venta)
        ultimo_pago = pagos[-1] if pagos else None

        pago_out = None
        if ultimo_pago:
            pago_out = PagoRespuesta.model_validate(ultimo_pago, from_attributes=True)

        detalles_out = []
        for d in venta.detalles:
            detalles_out.append(
                DetalleVentaRespuesta.model_validate(d, from_attributes=True)
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

    def crear_venta(self, bd: Session, datos: VentaCreada):
        venta = Venta(cliente=datos.cliente, fecha_venta=date.today())

        productos_validados = []
        canntidades_acumuladas = {}

        for detalle_data in datos.detalles:
            if detalle_data.cantidad_producto <= 0:
                raise BusinessRuleError("La cantidad de producto debe ser mayor a cero")

            producto = producto_repositorio.obtener_por_id(bd, detalle_data.id_producto)
            acumulado = canntidades_acumuladas.get(producto.id_producto, 0) + detalle_data.cantidad_producto

            if acumulado > producto.stock:
                raise BusinessRuleError(
                    f"Stock insuficiente para '{producto.nombre_producto}':"
                    f" Disponible '{producto.stock}', solicitado'{acumulado}'"
                )
            canntidades_acumuladas[producto.id_producto] = acumulado
            productos_validados.append((producto, detalle_data))

        for producto, detalle_data in productos_validados:
            producto = producto_repositorio.obtener_por_id(bd, producto.id_producto)
            detalle = DetalleVenta(
                id_producto= producto.id_producto,
                id_venta= venta.id_venta,
                cantidad_producto= detalle_data.cantidad_producto,
                precio_unitario= producto.precio,
                subtotal= detalle_data.cantidad_producto * producto.precio,
                iva= 0.0,
                descuento= 0.0,
            )
            self.agregar_detalle(venta, detalle)
            producto.stock -= detalle_data.cantidad_producto
            producto_repositorio.actualizar(bd, producto.id_producto, producto)

        venta_guardada = venta_repositorio.crear_venta(bd, venta)
        return self.a_venta_out(bd, venta_guardada)

    def obtener_venta(self, bd: Session, id_venta: str):
        venta = venta_repositorio.obtener_por_id(bd, id_venta)
        return self.a_venta_out(bd, venta)

    def eliminar_venta(self, bd: Session, id_venta: str):
        venta = venta_repositorio.obtener_por_id(bd, id_venta)

    # TODO: 
        if pago_repositorio.existe_pago_exitoso(bd, id_venta):
            raise ConflictError("No se puede eliminar una venta que ya fue pagada")

        for detalle in venta.detalles:
            try:
                producto = producto_repositorio.obtener_por_id(bd, detalle.id_producto)
            except ResourceNotFoundError:
                producto = None

            if producto is not None:
                producto.stock += detalle.cantidad_producto
                producto_repositorio.actualizar(bd, producto.id_producto, producto)

        return venta_repositorio.eliminar_venta(bd, id_venta)

    def listar_venta(self, bd: Session, cliente: str = None, ordenar_por: str = None, direccion: str = "asc",
                    pagina: int = 1, limite: int = 20):
        if ordenar_por is not None and ordenar_por not in self.CAMPOS_ORDEN:
            raise BusinessRuleError(f"El campo '{ordenar_por}' no es valido para ordenar")
        ventas = venta_repositorio.listar_todas(bd)

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
        items = [self.a_venta_out(bd, v) for v in ventas_pagina]

        return PaginatedResponse(
            items= items,
            total= total,
            pagina= pagina,
            limite= limite,
            total_paginas= total_paginas,
        )

    def generar_boleta(self, bd: Session, id_venta: str):
        venta = venta_repositorio.obtener_por_id(bd, id_venta)
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
```


### `compose.yml`

```yaml
services:

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"
  api:
    build: .
    ports:
      - "8001:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    command: ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  adminer:
    image: adminer
    restart: unless-stopped
    ports:
      - 8080:8080

volumes:
  postgres_data:
```


### `migrations/env.py`

```python
import os

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.base_datos import Base
import app.models.categoria_modelos
import app.models.detalle_venta_modelos
import app.models.pago_modelos
import app.models.producto_modelos
import app.models.venta_modelos

target_metadata = Base.metadata

database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```


### `migrations/script.py.mako`

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
```


### `migrations/versions/d558a2aa70ae_crear_esquema_inicial.py`

```python
"""crear esquema inicial

Revision ID: d558a2aa70ae
Revises: 
Create Date: 2026-10-31 13:41:48.546119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd558a2aa70ae'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categorias',
    sa.Column('id_categoria', sa.String(), nullable=False),
    sa.Column('nombre_categoria', sa.String(length=50), nullable=False),
    sa.Column('descripcion', sa.String(length=255), nullable=False),
    sa.Column('activa', sa.Boolean(), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
    sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id_categoria')
    )
    op.create_index(op.f('ix_categorias_id_categoria'), 'categorias', ['id_categoria'], unique=False)
    op.create_table('ventas',
    sa.Column('id_venta', sa.String(), nullable=False),
    sa.Column('cliente', sa.String(length=90), nullable=False),
    sa.Column('fecha_venta', sa.Date(), nullable=False),
    sa.Column('total', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id_venta')
    )
    op.create_index(op.f('ix_ventas_id_venta'), 'ventas', ['id_venta'], unique=False)
    op.create_table('pagos',
    sa.Column('id_pago', sa.String(), nullable=False),
    sa.Column('id_venta', sa.String(), nullable=False),
    sa.Column('fecha_pago', sa.Date(), nullable=False),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.Column('metodo_pago', sa.String(length=30), nullable=False),
    sa.Column('estado_pago', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['id_venta'], ['ventas.id_venta'], ),
    sa.PrimaryKeyConstraint('id_pago')
    )
    op.create_index(op.f('ix_pagos_id_pago'), 'pagos', ['id_pago'], unique=False)
    op.create_index(op.f('ix_pagos_id_venta'), 'pagos', ['id_venta'], unique=False)
    op.create_table('productos',
    sa.Column('id_producto', sa.String(), nullable=False),
    sa.Column('nombre_producto', sa.String(length=50), nullable=False),
    sa.Column('descripcion', sa.String(length=255), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('stock_minimo', sa.Integer(), nullable=False),
    sa.Column('id_categoria', sa.String(), nullable=False),
    sa.Column('precio', sa.Integer(), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
    sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['id_categoria'], ['categorias.id_categoria'], ),
    sa.PrimaryKeyConstraint('id_producto')
    )
    op.create_index(op.f('ix_productos_id_producto'), 'productos', ['id_producto'], unique=False)
    op.create_table('detalles_ventas',
    sa.Column('id_detalle', sa.String(), nullable=False),
    sa.Column('id_producto', sa.String(), nullable=False),
    sa.Column('id_venta', sa.String(), nullable=False),
    sa.Column('cantidad_producto', sa.Integer(), nullable=False),
    sa.Column('subtotal', sa.Float(), nullable=False),
    sa.Column('precio_unitario', sa.Float(), nullable=False),
    sa.Column('iva', sa.Float(), nullable=False),
    sa.Column('descuento', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id_producto'], ),
    sa.ForeignKeyConstraint(['id_venta'], ['ventas.id_venta'], ),
    sa.PrimaryKeyConstraint('id_detalle')
    )
    op.create_index(op.f('ix_detalles_ventas_id_detalle'), 'detalles_ventas', ['id_detalle'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_detalles_ventas_id_detalle'), table_name='detalles_ventas')
    op.drop_table('detalles_ventas')
    op.drop_index(op.f('ix_productos_id_producto'), table_name='productos')
    op.drop_table('productos')
    op.drop_index(op.f('ix_pagos_id_venta'), table_name='pagos')
    op.drop_index(op.f('ix_pagos_id_pago'), table_name='pagos')
    op.drop_table('pagos')
    op.drop_index(op.f('ix_ventas_id_venta'), table_name='ventas')
    op.drop_table('ventas')
    op.drop_index(op.f('ix_categorias_id_categoria'), table_name='categorias')
    op.drop_table('categorias')
    # ### end Alembic commands ###
```


### `pyproject.toml`

```toml
[project]
name = "app"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "Benjamin-Alarcon", email = "balarcon2026@alu.uct.cl" }
]
requires-python = ">=3.14"
dependencies = [
    "alembic>=1.20.1",
    "fastapi>=0.141.1",
    "psycopg[binary]>=3.3.6",
    "pydantic>=2.13.5",
    "sqlalchemy>=2.1.5",
    "uvicorn>=0.52.4",
]

[project.scripts]
app = "app:main"

[build-system]
requires = ["uv_build>=0.12.5,<0.13.0"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-root = ""
```


### `tests/EVIDENCIA.md`

````markdown
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
````


### `tests/ejecutar_pruebas.sh`

```bash
#!/usr/bin/env bash
# Ejecuta tests/pruebas.http sobre una base SQLite aislada y temporal.
# Requisitos: uv, Node.js/npx, curl.
#
# Uso:
#   bash tests/ejecutar_pruebas.sh
#   PUERTO=8099 bash tests/ejecutar_pruebas.sh

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

DIR_EVIDENCIA="$RAIZ/tests/evidencia"
mkdir -p "$DIR_EVIDENCIA"
MARCA="$(date +%Y%m%d-%H%M%S)"
LOG="$DIR_EVIDENCIA/ejecucion-${MARCA}.log"
LOG_API="$DIR_EVIDENCIA/uvicorn-${MARCA}.log"

if ! command -v npx >/dev/null 2>&1; then
  echo "ERROR: se requiere Node.js/npx para ejecutar httpyac." | tee "$LOG"
  exit 1
fi

{
  echo "Fecha: $(date -Iseconds)"
  echo
} | tee "$LOG"

uv sync --quiet 2>&1 | tee -a "$LOG"

if [[ -z "${PUERTO:-}" ]]; then
  PUERTO="$("$RAIZ/.venv/bin/python" - <<'PY'
import socket
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    print(s.getsockname()[1])
PY
)"
fi

BASE_URL="http://127.0.0.1:${PUERTO}"
DB="$(mktemp /tmp/minimarket_pruebas_XXXXXX.db)"
export DATABASE_URL="sqlite:///${DB}"

PID=""
limpiar() {
  if [[ -n "$PID" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  rm -f "$DB"
}
trap limpiar EXIT INT TERM

{
  echo "Base de datos aislada: $DB"
  echo "URL base: $BASE_URL"
  echo
} | tee -a "$LOG"

.venv/bin/alembic upgrade head 2>&1 | tee -a "$LOG"

.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$PUERTO" >"$LOG_API" 2>&1 &
PID=$!

for _ in $(seq 1 60); do
  if curl -fsS "$BASE_URL/openapi.json" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if ! curl -fsS "$BASE_URL/openapi.json" >/dev/null 2>&1; then
  echo "ERROR: la API no arrancó. Revisa $LOG_API" | tee -a "$LOG"
  exit 1
fi

set +e
npx --yes httpyac send tests/pruebas.http --all --no-color --var baseUrl="$BASE_URL" 2>&1 | tee -a "$LOG"
ESTADO=${PIPESTATUS[0]}
set -e

{
  echo
  if [[ "$ESTADO" -eq 0 ]]; then
    echo "RESULTADO: todas las pruebas pasaron."
  else
    echo "RESULTADO: hubo pruebas fallidas (código $ESTADO)."
  fi
  echo "Log guardado en: $LOG"
} | tee -a "$LOG"

exit "$ESTADO"
```


### `tests/http-client.env.json`

```json
{
  "docker": { "baseUrl": "http://localhost:8001" },
  "pruebas": { "baseUrl": "http://127.0.0.1:8002" }
}
```


### `tests/pruebas.http`

```http
# Colección de pruebas reproducibles — Minimarket API
#
# Ejecutar con httpyac (CLI):
#   npx --yes httpyac send tests/pruebas.http --all --no-color
#
# O cambiar la URL base:
#   npx --yes httpyac send tests/pruebas.http --all --no-color --var baseUrl=http://localhost:8002
#   (también puede usarse --env pruebas con tests/http-client.env.json)
#
# La colección está pensada para httpyac: las aserciones con "??" son específicas de httpyac.
# Las variables {{$timestamp}} generan nombres únicos para poder repetir la colección sin
# chocar con datos de ejecuciones anteriores.
#
# Casos incluidos:
#   1. CRUD de categoría
#   2. CRUD de producto
#   3. Validación inválida (422)
#   4. Recurso inexistente (404)
#   5. Regla de negocio: stock insuficiente (400)
#   6. Consulta con filtro, orden y paginación
#   7. Persistencia de datos (crear y recuperar una venta)
#   8. Reglas de negocio de pago y conflicto al eliminar venta pagada

# baseUrl se define con --var o con tests/http-client.env.json.
@sufijo = {{$timestamp}}

###############################################################################
# CASO 1 — CRUD de categoría
# Entrada: POST con nombre único, GET, PATCH y DELETE.
# Esperado: 201 al crear, 200 al consultar/actualizar, 204 al eliminar y 404 después.
###############################################################################

# @name crearCategoriaCrud
POST {{baseUrl}}/categorias/
Content-Type: application/json

{
  "nombre_categoria": "Categoria CRUD {{sufijo}}",
  "descripcion": "Creada para el caso 1",
  "activa": true
}

?? status == 201
?? body id_categoria exists
?? body nombre_categoria includes CRUD

###

# @name obtenerCategoriaCrud
# @ref crearCategoriaCrud
GET {{baseUrl}}/categorias/{{crearCategoriaCrud.id_categoria}}

?? status == 200
?? body id_categoria exists
?? body cantidad_productos == 0

###

# @name actualizarCategoriaCrud
# @ref crearCategoriaCrud
PATCH {{baseUrl}}/categorias/{{crearCategoriaCrud.id_categoria}}
Content-Type: application/json

{
  "descripcion": "Categoria actualizada",
  "activa": false
}

?? status == 200
?? body descripcion includes actualizada
?? body activa == false

###

# @name eliminarCategoriaCrud
# @ref crearCategoriaCrud
DELETE {{baseUrl}}/categorias/{{crearCategoriaCrud.id_categoria}}

?? status == 204

###

# @name obtenerCategoriaEliminada
# @ref crearCategoriaCrud
GET {{baseUrl}}/categorias/{{crearCategoriaCrud.id_categoria}}

?? status == 404
?? js response.parsedBody.error.code == RESOURCE_NOT_FOUND

###############################################################################
# CASO 2 — CRUD de producto
# Entrada: categoría auxiliar, POST/GET/PATCH/DELETE de producto.
# Esperado: 201, 200, 200, 204 y 404 después de eliminar.
###############################################################################

# @name crearCategoriaProducto
POST {{baseUrl}}/categorias/
Content-Type: application/json

{
  "nombre_categoria": "Categoria Producto {{sufijo}}",
  "descripcion": "Categoría auxiliar para el caso 2",
  "activa": true
}

?? status == 201

###

# @name crearProductoCrud
# @ref crearCategoriaProducto
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Producto CRUD {{sufijo}}",
  "descripcion": "Creado para el caso 2",
  "stock": 10,
  "stock_minimo": 2,
  "id_categoria": "{{crearCategoriaProducto.id_categoria}}",
  "precio": 1500
}

?? status == 201
?? body id_producto exists
?? body stock == 10

###

# @name obtenerProductoCrud
# @ref crearProductoCrud
GET {{baseUrl}}/productos/{{crearProductoCrud.id_producto}}

?? status == 200
?? body stock == 10
?? body precio == 1500

###

# @name actualizarProductoCrud
# @ref crearProductoCrud
PATCH {{baseUrl}}/productos/{{crearProductoCrud.id_producto}}
Content-Type: application/json

{
  "stock": 7
}

?? status == 200
?? body stock == 7

###

# @name eliminarProductoCrud
# @ref crearProductoCrud
DELETE {{baseUrl}}/productos/{{crearProductoCrud.id_producto}}

?? status == 204

###

# @name obtenerProductoEliminado
# @ref crearProductoCrud
GET {{baseUrl}}/productos/{{crearProductoCrud.id_producto}}

?? status == 404
?? js response.parsedBody.error.code == RESOURCE_NOT_FOUND

###

# @name eliminarCategoriaProducto
# @ref crearCategoriaProducto
DELETE {{baseUrl}}/categorias/{{crearCategoriaProducto.id_categoria}}

?? status == 204

###############################################################################
# CASO 3 — Validación inválida
# Entrada: POST /productos/ con body vacío.
# Esperado: 422 VALIDATION_ERROR con detalles de campos faltantes.
###############################################################################

# @name productoInvalido
POST {{baseUrl}}/productos/
Content-Type: application/json

{}

?? status == 422
?? js response.parsedBody.error.code == VALIDATION_ERROR
?? js response.parsedBody.error.details.length > 0

###############################################################################
# CASO 4 — Recurso inexistente
# Entrada: GET de una categoría con UUID que no existe.
# Esperado: 404 RESOURCE_NOT_FOUND.
###############################################################################

# @name categoriaInexistente
GET {{baseUrl}}/categorias/00000000-0000-0000-0000-000000000000

?? status == 404
?? js response.parsedBody.error.code == RESOURCE_NOT_FOUND

###############################################################################
# CASO 5 — Regla de negocio: stock insuficiente
# Entrada: producto con stock 1 y venta que solicita 2 unidades.
# Esperado: 400 BUSINESS_RULE_VIOLATION.
###############################################################################

# @name crearCategoriaStock
POST {{baseUrl}}/categorias/
Content-Type: application/json

{
  "nombre_categoria": "Categoria Stock {{sufijo}}",
  "descripcion": "Categoría auxiliar para el caso 5",
  "activa": true
}

?? status == 201

###

# @name crearProductoStock
# @ref crearCategoriaStock
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Producto Stock {{sufijo}}",
  "descripcion": "Stock insuficiente para el caso 5",
  "stock": 1,
  "stock_minimo": 1,
  "id_categoria": "{{crearCategoriaStock.id_categoria}}",
  "precio": 1000
}

?? status == 201

###

# @name ventaSinStock
# @ref crearProductoStock
POST {{baseUrl}}/ventas
Content-Type: application/json

{
  "cliente": "Cliente Sin Stock {{sufijo}}",
  "detalles": [
    {
      "id_producto": "{{crearProductoStock.id_producto}}",
      "cantidad_producto": 2
    }
  ]
}

?? status == 400
?? js response.parsedBody.error.code == BUSINESS_RULE_VIOLATION

###

# @name limpiarProductoStock
# @ref crearProductoStock
DELETE {{baseUrl}}/productos/{{crearProductoStock.id_producto}}

?? status == 204

###

# @name limpiarCategoriaStock
# @ref crearCategoriaStock
DELETE {{baseUrl}}/categorias/{{crearCategoriaStock.id_categoria}}

?? status == 204

###############################################################################
# CASO 6 — Consulta con filtro, orden y paginación
# Entrada: 3 productos con precios 100, 300 y 200; filtro por nombre,
#          orden descendente por precio, página 1 con límite 2.
# Esperado: total 3, total_paginas 2, items [300, 200]; página 2 con [100].
###############################################################################

# @name crearCategoriaFiltro
POST {{baseUrl}}/categorias/
Content-Type: application/json

{
  "nombre_categoria": "Categoria Filtro {{sufijo}}",
  "descripcion": "Categoría auxiliar para el caso 6",
  "activa": true
}

?? status == 201

###

# @name crearProductoFiltroA
# @ref crearCategoriaFiltro
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Filtro-{{sufijo}}-A",
  "descripcion": "Producto A para filtro",
  "stock": 10,
  "stock_minimo": 1,
  "id_categoria": "{{crearCategoriaFiltro.id_categoria}}",
  "precio": 100
}

?? status == 201

###

# @name crearProductoFiltroB
# @ref crearCategoriaFiltro
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Filtro-{{sufijo}}-B",
  "descripcion": "Producto B para filtro",
  "stock": 10,
  "stock_minimo": 1,
  "id_categoria": "{{crearCategoriaFiltro.id_categoria}}",
  "precio": 300
}

?? status == 201

###

# @name crearProductoFiltroC
# @ref crearCategoriaFiltro
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Filtro-{{sufijo}}-C",
  "descripcion": "Producto C para filtro",
  "stock": 10,
  "stock_minimo": 1,
  "id_categoria": "{{crearCategoriaFiltro.id_categoria}}",
  "precio": 200
}

?? status == 201

###

# @name consultaFiltroPagina1
# @ref crearProductoFiltroA
# @ref crearProductoFiltroB
# @ref crearProductoFiltroC
GET {{baseUrl}}/productos/?nombre=Filtro-{{sufijo}}&ordenar_por=precio&direccion=desc&pagina=1&limite=2

?? status == 200
?? js response.parsedBody.total == 3
?? js response.parsedBody.total_paginas == 2
?? js response.parsedBody.pagina == 1
?? js response.parsedBody.limite == 2
?? js response.parsedBody.items.length == 2
?? js response.parsedBody.items[0].precio == 300
?? js response.parsedBody.items[1].precio == 200

###

# @name consultaFiltroPagina2
# @ref crearProductoFiltroA
# @ref crearProductoFiltroB
# @ref crearProductoFiltroC
GET {{baseUrl}}/productos/?nombre=Filtro-{{sufijo}}&ordenar_por=precio&direccion=desc&pagina=2&limite=2

?? status == 200
?? js response.parsedBody.total == 3
?? js response.parsedBody.total_paginas == 2
?? js response.parsedBody.items.length == 1
?? js response.parsedBody.items[0].precio == 100

###

# @name limpiarProductoFiltroA
# @ref crearProductoFiltroA
DELETE {{baseUrl}}/productos/{{crearProductoFiltroA.id_producto}}

?? status == 204

###

# @name limpiarProductoFiltroB
# @ref crearProductoFiltroB
DELETE {{baseUrl}}/productos/{{crearProductoFiltroB.id_producto}}

?? status == 204

###

# @name limpiarProductoFiltroC
# @ref crearProductoFiltroC
DELETE {{baseUrl}}/productos/{{crearProductoFiltroC.id_producto}}

?? status == 204

###

# @name limpiarCategoriaFiltro
# @ref crearCategoriaFiltro
DELETE {{baseUrl}}/categorias/{{crearCategoriaFiltro.id_categoria}}

?? status == 204

###############################################################################
# CASO 7 — Persistencia de datos
# Entrada: crear categoría, producto y venta; luego recuperar la venta por su ID.
# Esperado: la venta creada se puede leer después con el mismo cliente y total,
#           lo que demuestra que los datos quedaron persistidos en la base.
###############################################################################

# @name crearCategoriaPersistencia
POST {{baseUrl}}/categorias/
Content-Type: application/json

{
  "nombre_categoria": "Categoria Persistencia {{sufijo}}",
  "descripcion": "Categoría auxiliar para el caso 7",
  "activa": true
}

?? status == 201

###

# @name crearProductoPersistencia
# @ref crearCategoriaPersistencia
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Producto Persistencia {{sufijo}}",
  "descripcion": "Producto para el caso 7",
  "stock": 5,
  "stock_minimo": 1,
  "id_categoria": "{{crearCategoriaPersistencia.id_categoria}}",
  "precio": 1000
}

?? status == 201

###

# @name crearVentaPersistencia
# @ref crearProductoPersistencia
POST {{baseUrl}}/ventas
Content-Type: application/json

{
  "cliente": "Cliente Persistencia {{sufijo}}",
  "detalles": [
    {
      "id_producto": "{{crearProductoPersistencia.id_producto}}",
      "cantidad_producto": 2
    }
  ]
}

?? status == 201
?? body id_venta exists
?? js response.parsedBody.total == 2000
?? js response.parsedBody.detalles.length == 1

###

# @name leerVentaPersistida
# @ref crearVentaPersistencia
GET {{baseUrl}}/ventas/{{crearVentaPersistencia.id_venta}}

?? status == 200
?? js response.parsedBody.id_venta exists
?? js response.parsedBody.total == 2000
?? js response.parsedBody.cliente includes Persistencia
?? js response.parsedBody.detalles.length == 1

###

# @name boletaVentaPersistida
# @ref crearVentaPersistencia
GET {{baseUrl}}/ventas/{{crearVentaPersistencia.id_venta}}/boleta

?? status == 200
?? js response.parsedBody.total == 2000
?? js response.parsedBody.items.length == 1

###

# @name limpiarVentaPersistencia
# @ref crearVentaPersistencia
DELETE {{baseUrl}}/ventas/{{crearVentaPersistencia.id_venta}}

?? status == 204

###

# @name limpiarProductoPersistencia
# @ref crearProductoPersistencia
DELETE {{baseUrl}}/productos/{{crearProductoPersistencia.id_producto}}

?? status == 204

###

# @name limpiarCategoriaPersistencia
# @ref crearCategoriaPersistencia
DELETE {{baseUrl}}/categorias/{{crearCategoriaPersistencia.id_categoria}}

?? status == 204

###############################################################################
# CASO 8 — Reglas de negocio de pago
# Entrada: venta con total 100; pago con monto incorrecto, pago correcto,
#          segundo pago sobre la misma venta e intento de eliminar la venta pagada.
# Esperado: 400 por monto incorrecto, 201 al pagar, 400 por pago duplicado y
#           409 al intentar eliminar una venta ya pagada.
# Nota: este caso deja una venta pagada en la base aislada de pruebas; el script
#       de ejecución elimina la base completa al terminar.
###############################################################################

# @name crearCategoriaPago
POST {{baseUrl}}/categorias/
Content-Type: application/json

{
  "nombre_categoria": "Categoria Pago {{sufijo}}",
  "descripcion": "Categoría auxiliar para el caso 8",
  "activa": true
}

?? status == 201

###

# @name crearProductoPago
# @ref crearCategoriaPago
POST {{baseUrl}}/productos/
Content-Type: application/json

{
  "nombre_producto": "Producto Pago {{sufijo}}",
  "descripcion": "Producto para el caso 8",
  "stock": 10,
  "stock_minimo": 1,
  "id_categoria": "{{crearCategoriaPago.id_categoria}}",
  "precio": 100
}

?? status == 201

###

# @name crearVentaPago
# @ref crearProductoPago
POST {{baseUrl}}/ventas
Content-Type: application/json

{
  "cliente": "Cliente Pago {{sufijo}}",
  "detalles": [
    {
      "id_producto": "{{crearProductoPago.id_producto}}",
      "cantidad_producto": 1
    }
  ]
}

?? status == 201
?? js response.parsedBody.total == 100

###

# @name pagoMontoIncorrecto
# @ref crearVentaPago
POST {{baseUrl}}/pagos
Content-Type: application/json

{
  "id_venta": "{{crearVentaPago.id_venta}}",
  "monto": 50,
  "metodo_pago": "debito"
}

?? status == 400
?? js response.parsedBody.error.code == BUSINESS_RULE_VIOLATION

###

# @name pagoCorrecto
# @ref crearVentaPago
POST {{baseUrl}}/pagos
Content-Type: application/json

{
  "id_venta": "{{crearVentaPago.id_venta}}",
  "monto": 100,
  "metodo_pago": "debito"
}

?? status == 201
?? body id_pago exists
?? js response.parsedBody.estado_pago == exitoso
?? js response.parsedBody.id_venta exists

###

# @name pagoDuplicado
# @ref crearVentaPago
POST {{baseUrl}}/pagos
Content-Type: application/json

{
  "id_venta": "{{crearVentaPago.id_venta}}",
  "monto": 100,
  "metodo_pago": "debito"
}

?? status == 400
?? js response.parsedBody.error.code == BUSINESS_RULE_VIOLATION

###

# @name obtenerPagoCreado
# @ref pagoCorrecto
GET {{baseUrl}}/pagos/{{pagoCorrecto.id_pago}}

?? status == 200
?? js response.parsedBody.id_pago exists
?? js response.parsedBody.estado_pago == exitoso

###

# @name ventaConPago
# @ref crearVentaPago
# @ref pagoCorrecto
GET {{baseUrl}}/ventas/{{crearVentaPago.id_venta}}

?? status == 200
?? js response.parsedBody.pago.id_pago exists
?? js response.parsedBody.pago.estado_pago == exitoso

###

# @name eliminarVentaPagada
# @ref crearVentaPago
# @ref pagoCorrecto
DELETE {{baseUrl}}/ventas/{{crearVentaPago.id_venta}}

?? status == 409
?? js response.parsedBody.error.code == CONFLICT
```


### `uv.lock`

```toml
version = 1
revision = 3
requires-python = ">=3.14"

[[package]]
name = "alembic"
version = "1.20.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "mako" },
    { name = "sqlalchemy" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/93/1c/00909e0fbebad2121d916fdcab044cae988146680e9ee4387ba25fef8747/alembic-1.20.1.tar.gz", hash = "sha256:83490def1f723413db5096591f7609ac52544805be93849170088ed04f5a2e0b", size = 2103576, upload-time = "2026-10-22T03:24:35.93Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/11/3c/8740f5b4e1bd57333e4f84265b9b6363da4f7cf70f5622dd1e2fde7a0bd5/alembic-1.20.1-py3-none-any.whl", hash = "sha256:9970712cfb81ea26c8658d378aaa5b8f6ff9146e5bb111d70497c164016cf598", size = 270355, upload-time = "2026-10-22T03:24:37.667Z" },
]

[[package]]
name = "annotated-doc"
version = "0.0.5"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/5a/8e/38aa427ed5402449e226975b649c5dc73ccadfefeb95e6aecb8f8ea4b6b6/annotated_doc-0.0.5.tar.gz", hash = "sha256:c7e58ce09192557605d8bbd92836d7e1d520ac9580096042c0bfd197efacf1bb", size = 10758, upload-time = "2026-07-28T13:50:58.129Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3e/30/e900b21425a860e195f32e37657aa1f7c7f2b1bfb26f03ca209b90933c06/annotated_doc-0.0.5-py3-none-any.whl", hash = "sha256:117bac03a25ede5df5440e855b32d556049ca169ead221505badf432fed4b101", size = 5302, upload-time = "2026-07-28T13:50:57.239Z" },
]

[[package]]
name = "annotated-types"
version = "0.8.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/5f/56/a8120250d128bed162cd73c76d45f6ef9991f3e068f62a8ee060afa3104a/annotated_types-0.8.0.tar.gz", hash = "sha256:13b2beaad985e05e2d6407ee4c4f35590b11f8d693a258a561055cac8f64cab7", size = 15893, upload-time = "2026-07-23T20:16:13.995Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/99/91/8acff4f5e50511b911bbccb72b8628a49c68ce14148cd9f6431094859a90/annotated_types-0.8.0-py3-none-any.whl", hash = "sha256:f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0", size = 13427, upload-time = "2026-07-23T20:16:12.938Z" },
]

[[package]]
name = "anyio"
version = "4.15.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "idna" },
    { name = "typing-extensions", marker = "python_full_version < '3.15'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ea/9a/c15a60547004a3f3cea20296c934f827ddd7bdba225a2e7e9fcb5ec48c80/anyio-4.15.0.tar.gz", hash = "sha256:b5c620ed540725e2579c31b17bb995b3bf02c9281c9cace04c7d186380bab85e", size = 276504, upload-time = "2026-09-02T21:46:36.957Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/21/a6/2b21ce5ebe4d8938a247c9b0dbb7271566ae559b01795c83ea4bb2660ed7/anyio-4.15.0-py3-none-any.whl", hash = "sha256:7ecd9937369ffce8bba0b5ccb9b3a9507b101b0ed50256aecfbab27e6c2acb99", size = 131908, upload-time = "2026-09-02T21:46:35.485Z" },
]

[[package]]
name = "app"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "alembic" },
    { name = "fastapi" },
    { name = "psycopg", extra = ["binary"] },
    { name = "pydantic" },
    { name = "sqlalchemy" },
    { name = "uvicorn" },
]

[package.metadata]
requires-dist = [
    { name = "alembic", specifier = ">=1.20.1" },
    { name = "fastapi", specifier = ">=0.141.1" },
    { name = "psycopg", extras = ["binary"], specifier = ">=3.3.6" },
    { name = "pydantic", specifier = ">=2.13.5" },
    { name = "sqlalchemy", specifier = ">=2.1.5" },
    { name = "uvicorn", specifier = ">=0.52.4" },
]

[[package]]
name = "click"
version = "8.5.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/c7/0e/7fa0ef50764b67090eca4114772a2abf8b6148198475e54c660b97caeee6/click-8.5.0.tar.gz", hash = "sha256:ba0d2089de75ea0310e2dde03160e6ca10009947fb95a182f9b54021bb272e34", size = 382235, upload-time = "2026-08-26T13:33:14.56Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/58/50/6c0d534c5f134586a8e1ba4e330569e32f057e33372ae556463212fb4cd3/click-8.5.0-py3-none-any.whl", hash = "sha256:255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360", size = 125251, upload-time = "2026-08-26T13:33:12.928Z" },
]

[[package]]
name = "fastapi"
version = "0.141.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "annotated-doc" },
    { name = "pydantic" },
    { name = "starlette" },
    { name = "typing-extensions" },
    { name = "typing-inspection" },
]
sdist = { url = "https://files.pythonhosted.org/packages/8a/02/91e3416a8fdd715abb903a952a6bec7cdd8d14eed55d415fc8595524c319/fastapi-0.141.1.tar.gz", hash = "sha256:e8822fc40db1e1858054d7a949a888695bc9bdce70139178e33bd2871a453ca1", size = 425799, upload-time = "2026-07-29T17:18:05.568Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/03/10388a42375ee7e4ac9b94eb2c5c569c8b5795e377e701c9ac3ad63de890/fastapi-0.141.1-py3-none-any.whl", hash = "sha256:bfb91aa2d334c61cb35ba9a116fc123b3d3df31640b801cf57a7a78ec3f603b3", size = 131954, upload-time = "2026-07-29T17:18:04.364Z" },
]

[[package]]
name = "h11"
version = "0.16.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/01/ee/02a2c011bdab74c6fb3c75474d40b3052059d95df7e73351460c8588d963/h11-0.16.0.tar.gz", hash = "sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1", size = 101250, upload-time = "2025-04-24T03:35:25.427Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl", hash = "sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86", size = 37515, upload-time = "2025-04-24T03:35:24.344Z" },
]

[[package]]
name = "idna"
version = "3.19"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/5f/f7/abb373e5757eaec4b922b92f97ec8d6d7e057cf06778247604fbc4e7c3f3/idna-3.19.tar.gz", hash = "sha256:5e0811a4383b21dc5838069f801c4fb62113b7447663d2530d2bd6e77b49bf15", size = 215237, upload-time = "2026-08-18T05:14:24.27Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/57/b0/0e52c878c53f245edd3a11020f20979b3f490f245af532c7cae3027754b5/idna-3.19-py3-none-any.whl", hash = "sha256:815e7be7a7806d54abb586dc943addc79e8b2ee16915059658cbeff4b1b43bf4", size = 68550, upload-time = "2026-08-18T05:14:22.343Z" },
]

[[package]]
name = "mako"
version = "1.4.3"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "markupsafe" },
]
sdist = { url = "https://files.pythonhosted.org/packages/5a/09/e07c4b5579a79f4b16f8d4f29f6c54514ac787c4ad506b8c4f28a0e6b0bf/mako-1.4.3.tar.gz", hash = "sha256:cd6537fe88d5fec315c55c2f8529bc4ce7a9a352ad7db3eeaa6a66e2dd4ec37a", size = 412799, upload-time = "2026-09-22T20:54:31.509Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6d/a0/053d6af3e8f871e0073b4a36732d9e65be77a72e5434c31b94f6af78a6bb/mako-1.4.3-py3-none-any.whl", hash = "sha256:723296007c870bfd6b3f0c3230dba7198096e5269297ebf5e4eff9e7ffa39d4f", size = 80164, upload-time = "2026-09-22T20:54:33.128Z" },
]

[[package]]
name = "markupsafe"
version = "3.0.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/38/9b/e422a865e1d5d57d0e509b4e0bf1c1a70a7f6382c29a5aa428df994c8bc8/markupsafe-3.0.4.tar.gz", hash = "sha256:2e9ad7dd851bf45fab9f75cbff4cb493fee9979e8d8c7c9c3ee119022518edd6", size = 153777, upload-time = "2026-10-02T23:07:22.29Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/5c/c3/a944f3b0df22bd129e96915b9f4e98d2eeca6516687d7618304a966c3c74/markupsafe-3.0.4-cp314-cp314-android_24_arm64_v8a.whl", hash = "sha256:4ed644d75aa94a2baf7ec3a96eaa160ea58c742eb9d27c6506053c5c40fc84ed", size = 12787, upload-time = "2026-10-02T23:05:30.971Z" },
    { url = "https://files.pythonhosted.org/packages/d4/d6/a44863f69d88b6c7e27889108f70d47aed259edf89d5df3c5fca1eac87d6/markupsafe-3.0.4-cp314-cp314-android_24_x86_64.whl", hash = "sha256:6d2a9efe686f9de00d0d1ea32a4a5a86d558a2277501bd78d964214eab625e59", size = 12525, upload-time = "2026-10-02T23:05:32.263Z" },
    { url = "https://files.pythonhosted.org/packages/17/8f/168ba80e532dd6a93f96f8f706f1ad41d7990b6e1aeedc1cc0d211a33497/markupsafe-3.0.4-cp314-cp314-ios_13_0_arm64_iphoneos.whl", hash = "sha256:8781a792a070cf2bd1b86d3aa943894115faaba6e88122a7bf32d62072742453", size = 11589, upload-time = "2026-10-02T23:05:33.251Z" },
    { url = "https://files.pythonhosted.org/packages/32/b3/aa2c95a574d3af39403a469b295886eb9b6d448da568cbebb5a2cbfdc2e5/markupsafe-3.0.4-cp314-cp314-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:971a3bbb75d97ae4e2e8f7d4834236f86f85f0c85e04ab2e191db1123b04f80b", size = 11801, upload-time = "2026-10-02T23:05:34.315Z" },
    { url = "https://files.pythonhosted.org/packages/60/d0/34b810107d83840e768bf485de795893ebbae35b26ab061b487adfa0a692/markupsafe-3.0.4-cp314-cp314-ios_13_0_x86_64_iphonesimulator.whl", hash = "sha256:8909c2f1c6dd65e054ac4b573a91c8384d1492281e55d82d159d653f7a13adf6", size = 11447, upload-time = "2026-10-02T23:05:35.302Z" },
    { url = "https://files.pythonhosted.org/packages/6c/ab/2f8488f0f817a39fca068d2b17daf446bf5cdb3eae28c3720af534d873b4/markupsafe-3.0.4-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:4cf3468d5ec187ffffcaca8e61929a37448f215dafc1386a12c750a72fe53634", size = 11722, upload-time = "2026-10-02T23:05:36.363Z" },
    { url = "https://files.pythonhosted.org/packages/ad/40/e2d117b048d47282ade906fbfd92814cbee5647afc13fda88a3406039372/markupsafe-3.0.4-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:52704c5d36eb6dda8866493decd61111fff86244c9b1ad225ca01b9e91e5970f", size = 12061, upload-time = "2026-10-02T23:05:37.397Z" },
    { url = "https://files.pythonhosted.org/packages/9a/a8/73a81135e85ba66217f5af7facb03bbb386807e1a729ab64532e4c802652/markupsafe-3.0.4-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:1caa2fa5a6184fb233153b35f654e6687bd555476f6170f29d8ee9be1a8b0af9", size = 24434, upload-time = "2026-10-02T23:05:38.407Z" },
    { url = "https://files.pythonhosted.org/packages/ac/ca/fa9216dd01efee2dfdacafe7df32b4d0170fbac694b0c258a193d6e53999/markupsafe-3.0.4-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:387d8cd30e69b3f0a72877b9ae717033396404e19095b17fe89753a981fda44f", size = 27183, upload-time = "2026-10-02T23:05:39.581Z" },
    { url = "https://files.pythonhosted.org/packages/fa/4e/a469509e538d37af51103b17b073126973f2b1cbf197ff32c7ddf025cfe5/markupsafe-3.0.4-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:051417f74bcaaefa316276e0ff723f541616ca51043d070da00249d9bddd3e3c", size = 24813, upload-time = "2026-10-02T23:05:40.671Z" },
    { url = "https://files.pythonhosted.org/packages/8f/db/d7282caf7ab03af44d5d6fdbaa019b35c7d7f1c90588b839c07cba640d6a/markupsafe-3.0.4-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:a8e9f292fcda89b324f2f5c91d13f1424a153e40fc2756f38ee23b15835ff300", size = 23049, upload-time = "2026-10-02T23:05:41.864Z" },
    { url = "https://files.pythonhosted.org/packages/30/f3/b6a425206e6964efda6acee544d0eb01d1501784d0b8e2dcc74986f33b17/markupsafe-3.0.4-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:df1ae86ff54725a01fa1a0510b914ca53a161b7050be74f6204e24aded5971d0", size = 22088, upload-time = "2026-10-02T23:05:43.014Z" },
    { url = "https://files.pythonhosted.org/packages/ea/8a/84d3582fc1f0d5bd466cdf2eebf175e172158a6e70701aacec1de1b35430/markupsafe-3.0.4-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:8965520ac587c94a4ac48b729be3d8b8de00af39699b17585dfb599babe77977", size = 23846, upload-time = "2026-10-02T23:05:44.098Z" },
    { url = "https://files.pythonhosted.org/packages/1c/65/db101cce51b7ba4864ac491a9859d297dd1adf0e55b103fee9db9c47c527/markupsafe-3.0.4-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:340cbb1957ba99929cbf19a75626d36ba1ae21d1730b287d1cf7f824a20c4fc7", size = 22674, upload-time = "2026-10-02T23:05:45.23Z" },
    { url = "https://files.pythonhosted.org/packages/e0/49/ddee9813d71db0c7a5c9d97c832125e6758a0c844777f1cf076569bb0e22/markupsafe-3.0.4-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:3a93d9616ddecfb393727a0041a562cf0b15a244e20f2bd25efc7949be4c4f17", size = 24104, upload-time = "2026-10-02T23:05:46.398Z" },
    { url = "https://files.pythonhosted.org/packages/aa/0e/7d8518d726726870a2399d69fd30d0fa36c5e57a2132c336b58d7c491073/markupsafe-3.0.4-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:d2e56fd3b00222722abfb3f5f0759ddbae4b90811b5ad4343c64030ad1bde70c", size = 21637, upload-time = "2026-10-02T23:05:47.48Z" },
    { url = "https://files.pythonhosted.org/packages/b4/b0/b505e8a361ba557dbf3b3aa7331ea39b00d2022a26e925ff8463b9714bb3/markupsafe-3.0.4-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:0d9c47709875fdb321452056622e930c52afbc07a7d780762fbb8b4d91ce6fa4", size = 23081, upload-time = "2026-10-02T23:05:48.611Z" },
    { url = "https://files.pythonhosted.org/packages/1c/ea/9cc3cea873f980c75cbdb6f4277ce30ee955de38be0b3d02f14c108e0698/markupsafe-3.0.4-cp314-cp314-win32.whl", hash = "sha256:38fc55594dab834470b6733dead2ee9e3f657fb0608c769dcafa0ba5ab52f45c", size = 14272, upload-time = "2026-10-02T23:05:49.707Z" },
    { url = "https://files.pythonhosted.org/packages/80/f0/5792ff768a410f93ee3f84fc19345295ffc352d2c936b424cb37e514714c/markupsafe-3.0.4-cp314-cp314-win_amd64.whl", hash = "sha256:c1bc67752d5f21013cfe430df4062441714eab79f65a6a05e01505957e9c35fe", size = 14501, upload-time = "2026-10-02T23:05:50.788Z" },
    { url = "https://files.pythonhosted.org/packages/5f/cf/3d074a8edffcc6899355232ff2543ae8d929733239596423b7db79698bc9/markupsafe-3.0.4-cp314-cp314-win_arm64.whl", hash = "sha256:7e1636da3d8dfc220b6dd10264db5f2b165e4888c4518594898fbe381049af8a", size = 14364, upload-time = "2026-10-02T23:05:51.857Z" },
    { url = "https://files.pythonhosted.org/packages/d9/31/87ce42159aae2163cf3bbbd0c44bc87780510eecab1ea3859099aed95dcb/markupsafe-3.0.4-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:805c8b84534fa10891890f0e4be39f3a99e94615d93e8836bf9fa1fdca2feeb2", size = 11759, upload-time = "2026-10-02T23:05:52.951Z" },
    { url = "https://files.pythonhosted.org/packages/5f/53/b047207eeb7752e960aca3eb1df5fb7eefa7dd4c62ac49bb156456c8a702/markupsafe-3.0.4-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:fa95848c929b6a75f6848d3c9793e59db365ee436776e57db835cdbfa79ba977", size = 12096, upload-time = "2026-10-02T23:05:54.066Z" },
    { url = "https://files.pythonhosted.org/packages/ee/51/4326c88a13c7b755657d44b4bb986f8c3d9843ecba7e22d98661d87f9a57/markupsafe-3.0.4-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:e916035e3e9930cbdfdd10abf48861340221857f45509565898e012263f7b289", size = 25699, upload-time = "2026-10-02T23:05:55.15Z" },
    { url = "https://files.pythonhosted.org/packages/f2/bb/990581b7474bfcf2cf34bed6ba5ea23bd87adb9d671213d68e88620e7a6b/markupsafe-3.0.4-cp314-cp314t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:b4d12837e0203bbace818ff4a7461afdcd78bcd782351cea148139180d7bcffe", size = 27804, upload-time = "2026-10-02T23:05:56.29Z" },
    { url = "https://files.pythonhosted.org/packages/6b/89/89491878c28e8291f5aa2fffe2c2d57230d10ae366d55dd810b840513d78/markupsafe-3.0.4-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:5086f9975abb1ab531ee6afca1761e4b59a19b446f3f6522ed776963228cfe5a", size = 25912, upload-time = "2026-10-02T23:05:57.416Z" },
    { url = "https://files.pythonhosted.org/packages/30/77/680998b54efdea06fc114565cd739b6d059f826a0279219b218dfa750d29/markupsafe-3.0.4-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:b4a635a0487774f841cb1fb62e907e7195cc95bc761e053184b8acc3ceb20733", size = 23623, upload-time = "2026-10-02T23:05:58.557Z" },
    { url = "https://files.pythonhosted.org/packages/ae/75/2709f5ac5de9467b40b10e2bb8f89cc63dfb74582e09aa734b1124a217de/markupsafe-3.0.4-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:cb96e6e088d6cf71c1ea977510948320234824cf226e32f6f6e044f7a9c82b34", size = 23301, upload-time = "2026-10-02T23:05:59.94Z" },
    { url = "https://files.pythonhosted.org/packages/a0/c8/39eadc6c5b14c9c7679bfb98f4d4c6a97863b5beb91839aca4d2d6e16e55/markupsafe-3.0.4-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:8b5d563170ff8ba3181caa967c99a3c804d1dedb702c7cb93a6a7c32247da978", size = 24950, upload-time = "2026-10-02T23:06:01.289Z" },
    { url = "https://files.pythonhosted.org/packages/1a/5e/01037f8a43e8ccb0bffb4fbdc5212db05bf080fdd7286cd392332d58128a/markupsafe-3.0.4-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:396ec4e65cc889f69786b3b89478b471cee5a3bcf468b9d9bb03e1a30fb291fc", size = 23330, upload-time = "2026-10-02T23:06:02.441Z" },
    { url = "https://files.pythonhosted.org/packages/d4/f4/23e83ce0596bb0cbe670502d31df8f757bbd01a392aa486fa3b40d1ed399/markupsafe-3.0.4-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:15ba9e28640feef770374b116a6f019c21f52404aeabe516aa7f800587b98cfc", size = 25239, upload-time = "2026-10-02T23:06:03.579Z" },
    { url = "https://files.pythonhosted.org/packages/88/5b/3708897368073cc683d524750474f41a77d2986152c380dcc55b20fdf340/markupsafe-3.0.4-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:d920abdfa61279ba1a2ef9484aab07bf03331f8c08a10120fa332353d06e6932", size = 22767, upload-time = "2026-10-02T23:06:04.699Z" },
    { url = "https://files.pythonhosted.org/packages/c6/61/ebda1307864b409e6b3115757a3d4a09cca46cfb6cc65191b5de226b424b/markupsafe-3.0.4-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:a9f54054101545a9a9cccefddf54316aa6e4491611fcbef9e91b3b6bebec04f6", size = 23668, upload-time = "2026-10-02T23:06:05.9Z" },
    { url = "https://files.pythonhosted.org/packages/09/15/98075cceac3b5ba0dbb8e4762a847be967d2befc349a2cf2d0ac77f62c9d/markupsafe-3.0.4-cp314-cp314t-win32.whl", hash = "sha256:12a606a492de952afcb43b59a14aaaaad120e708d3663dd0fdf2d738d427a691", size = 14301, upload-time = "2026-10-02T23:06:07.109Z" },
    { url = "https://files.pythonhosted.org/packages/0b/a3/768b560fcc4156685cb563d922b217810cfa7bc135773367f62f1f9d2078/markupsafe-3.0.4-cp314-cp314t-win_amd64.whl", hash = "sha256:a18f38cafc329bac5e3c2b96c765b4c96d3d103421ed22ab7988c1e3fce27464", size = 14526, upload-time = "2026-10-02T23:06:08.276Z" },
    { url = "https://files.pythonhosted.org/packages/93/63/da554b4c97a6b0ea3229ca7fe8cbfb620be81613d517f482e85958550537/markupsafe-3.0.4-cp314-cp314t-win_arm64.whl", hash = "sha256:eba154571c16e032112afac0dc2dfe9e63c2ceb7aedd07bb7eecf2ce26d4dd4c", size = 14421, upload-time = "2026-10-02T23:06:09.402Z" },
    { url = "https://files.pythonhosted.org/packages/a9/30/54d11c8ca027114898cab97421fb39e4ffd9ddf47cdbc44df2ec76722da9/markupsafe-3.0.4-cp315-cp315-android_24_arm64_v8a.whl", hash = "sha256:737c9c3981998eba27f11786f84fddcbabc74068b72a4a1f454ea02094b57b65", size = 12791, upload-time = "2026-10-02T23:06:10.485Z" },
    { url = "https://files.pythonhosted.org/packages/10/6d/97c913e253a14bd3cd0e15a5c56d13203b823fa7ee32498342896a072dc4/markupsafe-3.0.4-cp315-cp315-android_24_x86_64.whl", hash = "sha256:489505b03f692c3f376394e49194fa7a7f9e8558d6e293a7056a0032b0c38163", size = 12527, upload-time = "2026-10-02T23:06:11.834Z" },
    { url = "https://files.pythonhosted.org/packages/26/f9/b86d032042a4d597d9e1997f0e5f63a3eedaf11258e0a05760b0a0a826ea/markupsafe-3.0.4-cp315-cp315-ios_13_0_arm64_iphoneos.whl", hash = "sha256:077293e425f28ec737dbcad442a71752e28f8ae27cde3d68acd1fb212091cd92", size = 11602, upload-time = "2026-10-02T23:06:13.122Z" },
    { url = "https://files.pythonhosted.org/packages/f2/dc/73c14c1eedf0ac5fa3292ba43435e6c49d2c2050f33cebde541f8f4807f1/markupsafe-3.0.4-cp315-cp315-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:9348cbb300d224fe3b89793262cb093504d4ae927004468463f745188a193e4a", size = 11817, upload-time = "2026-10-02T23:06:14.227Z" },
    { url = "https://files.pythonhosted.org/packages/8f/69/2c2fcaa5fcee22d72c7819c0d536fd181c74a688e6143845419579cd2863/markupsafe-3.0.4-cp315-cp315-ios_13_0_x86_64_iphonesimulator.whl", hash = "sha256:b807e598953730f82e4eae3bd30f6a122cf6b31c398c6b504c0e04c13c170429", size = 11446, upload-time = "2026-10-02T23:06:15.574Z" },
    { url = "https://files.pythonhosted.org/packages/88/54/9e5ec76c62e6e2834d5a93623018c943e8b3bb41d663e3fd4c03303b9b85/markupsafe-3.0.4-cp315-cp315-macosx_10_15_x86_64.whl", hash = "sha256:799c39bdf5e2f1292fedd3009f7b3c9e760f10b2420cb9638d56920840ff6db8", size = 11719, upload-time = "2026-10-02T23:06:16.701Z" },
    { url = "https://files.pythonhosted.org/packages/96/24/3ec292b44064c16229e064d770b2625bd8ea941aa61f44905a9fa44942c0/markupsafe-3.0.4-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:ae9dcb8fbe244cb82f8a6458b455b927a03685e383d9bacf1ea5ce180b96dc97", size = 12075, upload-time = "2026-10-02T23:06:17.855Z" },
    { url = "https://files.pythonhosted.org/packages/aa/85/b64fdb1f304848518742136983c24e96d967bfb59a0ea160e92736901ab0/markupsafe-3.0.4-cp315-cp315-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4bced6e2a6dba6a28f7dd3c6ce14df1b2dd495923f16ea484cad03decd463b2b", size = 24656, upload-time = "2026-10-02T23:06:18.963Z" },
    { url = "https://files.pythonhosted.org/packages/9c/18/23997d4c65b355da6390d61cd56e0ab3befd6ba8dda25cb40c602bd0fa6b/markupsafe-3.0.4-cp315-cp315-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:3882fb412298575bae3b9c46868251f15cc69307359f87bb1b382e53d6e5a2c9", size = 27737, upload-time = "2026-10-02T23:06:20.117Z" },
    { url = "https://files.pythonhosted.org/packages/d4/36/35998dead3c6af88c38265a56e58100211f036234ab88eb2283fd4cbce44/markupsafe-3.0.4-cp315-cp315-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:04e7902ba80ee4bac1d50a549606527a1dcf0476cd81403db41099d3b60ec653", size = 25003, upload-time = "2026-10-02T23:06:21.284Z" },
    { url = "https://files.pythonhosted.org/packages/82/96/ef49135ce260db4ca4a12b119ed468449cd248db6b1468e2112b546d7a2e/markupsafe-3.0.4-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:925f929d6b59a8b3f8b8c6ac363cd0af7eecc81efb3071770b3c6717c450a369", size = 23111, upload-time = "2026-10-02T23:06:22.524Z" },
    { url = "https://files.pythonhosted.org/packages/50/7d/83126e338bd88c17a220668235368ad719fd4638e426739858cbb8508f77/markupsafe-3.0.4-cp315-cp315-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:f68edfc67aabac33708941f26f22a7b8e9f81429bc0cf249fcf7d66b23af8d19", size = 22403, upload-time = "2026-10-02T23:06:23.785Z" },
    { url = "https://files.pythonhosted.org/packages/83/dd/daf7e420de23c8206c365204e7b85e1251d8e19d34196a56336f316e5ed2/markupsafe-3.0.4-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:e5c802729725bd07e2bc3ab7b76dc7e0bbfc53129d8f1eb1c002c24cf774717e", size = 24083, upload-time = "2026-10-02T23:06:25.037Z" },
    { url = "https://files.pythonhosted.org/packages/19/3c/11eecdc06bc44ad5570350085b572ebf049e8f9a38d1ece6d76640b739cd/markupsafe-3.0.4-cp315-cp315-musllinux_1_2_armv7l.whl", hash = "sha256:55ffd6ce583d97dc71dc92e930324c8c0d25aea7e3ade6ae54ef77cedb096811", size = 22931, upload-time = "2026-10-02T23:06:26.328Z" },
    { url = "https://files.pythonhosted.org/packages/0d/9e/ac0fd77f2a726e56ecc3ca0235d095feace1358d1b822406c2a2ef26a4dc/markupsafe-3.0.4-cp315-cp315-musllinux_1_2_ppc64le.whl", hash = "sha256:2cb3dd71fc6be918ad4264346a8ed69485f9b7ed7bf35495d8e22807cd6b8bea", size = 24299, upload-time = "2026-10-02T23:06:27.742Z" },
    { url = "https://files.pythonhosted.org/packages/d7/09/c6bd842ad58ff5b3bc76eeed7e9a42a6f11adc5d090ec697b72c9672731e/markupsafe-3.0.4-cp315-cp315-musllinux_1_2_riscv64.whl", hash = "sha256:94f5407f7bc64fa6463906b896f9904beeeb7dd8dc116ee8e9056c8714ff9916", size = 21948, upload-time = "2026-10-02T23:06:29.274Z" },
    { url = "https://files.pythonhosted.org/packages/a3/46/82f586711fed61e86faa1ee1bc317d68cd45a10c8bdbe3f7d1fdf9026ad8/markupsafe-3.0.4-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:2dad610540cb2e6272855c178f08ae9a1c7ac258a7fb71660553a5f104b42741", size = 23150, upload-time = "2026-10-02T23:06:30.583Z" },
    { url = "https://files.pythonhosted.org/packages/19/2d/2dfdce99318abbfa26925195fbc17db188c46a1ec6457be121b6f9cfeb42/markupsafe-3.0.4-cp315-cp315-win32.whl", hash = "sha256:03470d1a8268e692ecf79ecd565593e59d44219377a7ead61f1f1b94c1f7ff6b", size = 14269, upload-time = "2026-10-02T23:06:31.949Z" },
    { url = "https://files.pythonhosted.org/packages/5b/ec/6000fd82e8791e58fcd0456ec20f098957e2b03d5ed02eb73241a577c0ba/markupsafe-3.0.4-cp315-cp315-win_amd64.whl", hash = "sha256:d882a373d8093c2941e01291b7ced96e9cbe4781da9a7751ca7e6c70385e5214", size = 14496, upload-time = "2026-10-02T23:06:33.258Z" },
    { url = "https://files.pythonhosted.org/packages/bc/66/e73bd5016421d5d6e2fb6de7dd609f9de020942ac8c626526bd8c6eeaf82/markupsafe-3.0.4-cp315-cp315-win_arm64.whl", hash = "sha256:353bd63081912ab8cfa6a0c7d185934cdf8426f04c618bba6bc4b394f2069b67", size = 14361, upload-time = "2026-10-02T23:06:34.539Z" },
    { url = "https://files.pythonhosted.org/packages/90/df/cb8c3dc98d313a951df2f8968f44e4cb5643df6d3cab749a530ce2f7d972/markupsafe-3.0.4-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:c61750fadcd119d0825bcb7d7d675dd264dcc89cc05292aab5be68ebdbb374ad", size = 11760, upload-time = "2026-10-02T23:06:35.807Z" },
    { url = "https://files.pythonhosted.org/packages/d6/bb/4af9b3ca0753d654ac75f9531d5bd741bb77ca6e696f36807c475ffc099a/markupsafe-3.0.4-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:1c0df495a977d10460a94941799c72d5b5ab03d3858d949b55b5a66c8f371c99", size = 12108, upload-time = "2026-10-02T23:06:37.089Z" },
    { url = "https://files.pythonhosted.org/packages/3f/d4/b56429313aee5fd59b079c3df5615299959e25e7113eb6d8caadbdd7d38a/markupsafe-3.0.4-cp315-cp315t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:02fa4acbc6a3fc5c693c34d4dd8c1130b7fe99cc915181b0ddd6f72aeb296002", size = 25762, upload-time = "2026-10-02T23:06:38.419Z" },
    { url = "https://files.pythonhosted.org/packages/65/f5/34c181e891aa4f7d59c918584672e0c5eb7fffe76c1387d1246008bf4081/markupsafe-3.0.4-cp315-cp315t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:05295589e619b9bed252a86b532b8e27350abc372d18ba89b59375325e91ec1e", size = 28400, upload-time = "2026-10-02T23:06:39.819Z" },
    { url = "https://files.pythonhosted.org/packages/ce/b5/ad14694fd0ac9a5ce30bc6498f2999378f418583dd1679cca5a1b512957e/markupsafe-3.0.4-cp315-cp315t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:be6cb0c799abb0e2ba3e618e6d28ddddf7e485f6c2ce938dfa237daf3905072c", size = 25946, upload-time = "2026-10-02T23:06:41.381Z" },
    { url = "https://files.pythonhosted.org/packages/d6/a8/26b606445387d0ceb1eb1f21840094b84e4e3c3c3983d80d10b89823b490/markupsafe-3.0.4-cp315-cp315t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:26e9867520db70d37f7fb421a7f0d8adb40171011fb84ce869afa1a83370dfa8", size = 23634, upload-time = "2026-10-02T23:06:42.748Z" },
    { url = "https://files.pythonhosted.org/packages/39/a2/b8814de672f1f0094d498bf646f2fec9d6356b503d28ef500b71c5095377/markupsafe-3.0.4-cp315-cp315t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:f03460ff076f70ab595bb45a0205ccea1971443575b6920c52e755dec2b3fbfe", size = 23488, upload-time = "2026-10-02T23:06:44.176Z" },
    { url = "https://files.pythonhosted.org/packages/db/c7/287223376fb73335a3cc5d6eb22c6ab01358cf33945a9c39c06b9dac3f4b/markupsafe-3.0.4-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:436e3ffc6310d3c41878c601db29098102fe5d8a467c49da4a4125254e0980f2", size = 25037, upload-time = "2026-10-02T23:06:45.646Z" },
    { url = "https://files.pythonhosted.org/packages/f9/29/4df8355e313426d19e62ba33e0253c009ca12a0894ee77d67fa67255361c/markupsafe-3.0.4-cp315-cp315t-musllinux_1_2_armv7l.whl", hash = "sha256:4e2c4809c14559aa7ef426f27fb35afbb38104c349a903bf8f3600456764bb38", size = 23543, upload-time = "2026-10-02T23:06:47.264Z" },
    { url = "https://files.pythonhosted.org/packages/71/e5/8377731e8495668dcc768f645e717df18318c841edaf023a99395f6da9b4/markupsafe-3.0.4-cp315-cp315t-musllinux_1_2_ppc64le.whl", hash = "sha256:da2af0d7aebfc2074080d72efa6ab8317c62481ef1f896f65d9999c1c01f4494", size = 25282, upload-time = "2026-10-02T23:06:48.795Z" },
    { url = "https://files.pythonhosted.org/packages/ed/5f/373456e37ceb1478d657d6fe769cbe0a39f0a8dfc1548eeb19c471eefdd9/markupsafe-3.0.4-cp315-cp315t-musllinux_1_2_riscv64.whl", hash = "sha256:aa2c838cc024642cc04c6854232f32b43e5e22833dd11119c1766c7873b8370d", size = 22993, upload-time = "2026-10-02T23:06:50.31Z" },
    { url = "https://files.pythonhosted.org/packages/d7/93/2cbd5628435afb6f541bbaced4bce0c2edac4b09a142e6e928b8b0da9858/markupsafe-3.0.4-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:b91cc9d336957239ff200f30097e6fea2dc6d6fb3c81e853eaa09eac904fd894", size = 23712, upload-time = "2026-10-02T23:06:51.759Z" },
    { url = "https://files.pythonhosted.org/packages/81/99/157e10966b033b363aeda5263e82596ee232a0b1d082fdbf90aa417ff083/markupsafe-3.0.4-cp315-cp315t-win32.whl", hash = "sha256:e49fb0d1ce92cfa0cb198cc5b1b11cdf9d0638658e2a2db2687e39db7c87fc78", size = 14300, upload-time = "2026-10-02T23:06:53.241Z" },
    { url = "https://files.pythonhosted.org/packages/33/05/55884815414c9706a23deca150b72c25a62109e65b0b6ce232077802c719/markupsafe-3.0.4-cp315-cp315t-win_amd64.whl", hash = "sha256:4f6e0852a0283b1b1fd776eeb7b766a5f440b3e2bd31ab51af3b400585f3965c", size = 14522, upload-time = "2026-10-02T23:06:54.729Z" },
    { url = "https://files.pythonhosted.org/packages/92/f9/ecbde7149e95b8a0f18e16d5d747f7dc06049d5da2e4f77f6f5e4a1f46a8/markupsafe-3.0.4-cp315-cp315t-win_arm64.whl", hash = "sha256:39dbacefc411633db5b4378b066a9aca70a3d7e2922c9e578d825f844026eeba", size = 14417, upload-time = "2026-10-02T23:06:56.246Z" },
]

[[package]]
name = "psycopg"
version = "3.3.6"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "tzdata", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/76/26/3ea4ca5eaea1c0debcdf7ee7c1613fbe721dc27a03c461c0817ffd8a0601/psycopg-3.3.6.tar.gz", hash = "sha256:c081f2250df751a943036e42db6df4571c66cd0aabe8291a7a506512b12007d2", size = 168171, upload-time = "2026-09-18T13:22:55.152Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/4e/de/748bd7609c71cae5d737f0ba9192f19329f70180ecda8fff3cac02c5abe3/psycopg-3.3.6-py3-none-any.whl", hash = "sha256:a1db9f7148b06a28606767efaca51fa6f9398c5c0a3810519be69d7000bdb631", size = 215490, upload-time = "2026-09-18T13:15:29.374Z" },
]

[package.optional-dependencies]
binary = [
    { name = "psycopg-binary", marker = "implementation_name != 'pypy'" },
]

[[package]]
name = "psycopg-binary"
version = "3.3.6"
source = { registry = "https://pypi.org/simple" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6d/b9/60711317c284a442511644ea7185b56ebe627606d6741e732cd16108c47b/psycopg_binary-3.3.6-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:b3f75dee0f9afafabe4edc52c4842f1e1878ed2069bd05b22d6fe961e97e4dba", size = 4720512, upload-time = "2026-09-18T13:20:29.278Z" },
    { url = "https://files.pythonhosted.org/packages/63/da/28befc84454cbc6374550de7746f591f8fe1b6165c1fce249652cc8291c4/psycopg_binary-3.3.6-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:5927b7ba63153cd8e9862987290a2b783a5c590daf2a4ef981700cc3569166d4", size = 4782318, upload-time = "2026-09-18T13:20:35.401Z" },
    { url = "https://files.pythonhosted.org/packages/a4/8a/0d21c2c833cdc0d4244c77e858e0ed37fa2abec2623be4fd686f617109ce/psycopg_binary-3.3.6-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:0bf08b749cc144f33b44a91b78e3f71c60eb07963746a0df5a100b36ce3d7475", size = 5567460, upload-time = "2026-09-18T13:20:41.902Z" },
    { url = "https://files.pythonhosted.org/packages/49/6d/7692d0d4e656b6cc9868d8acc2e3b42f17a0db4a625400a6d093cb0533a1/psycopg_binary-3.3.6-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:31cd942c23f613276b81a6e6598cefa12960058b0f46e1e874b540c793f6aca5", size = 5246902, upload-time = "2026-09-18T13:20:47.661Z" },
    { url = "https://files.pythonhosted.org/packages/d4/c1/b8a1f18fb1b7558a17f57f7cb3fc8bc93189feea2958925950b3acb15743/psycopg_binary-3.3.6-cp314-cp314-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4690cf67738f0e0e49a32aeec99bf0e4595cc2b4f1af984a4345394b1dcff91a", size = 6847192, upload-time = "2026-09-18T13:20:56.874Z" },
    { url = "https://files.pythonhosted.org/packages/a5/76/404f33519167c65cca88ec4998776f1dbebccc301ee977f0e62c47fb0826/psycopg_binary-3.3.6-cp314-cp314-manylinux_2_38_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:ad1c785e784cfd87e8436c6b7702f2d321fc39601bbaf29bc63a41a867091638", size = 5079573, upload-time = "2026-09-18T13:21:04.155Z" },
    { url = "https://files.pythonhosted.org/packages/f0/d9/79e8fbc8f37262a415f3550f0bcc5f98037442bf3d12ef6cbae2056655ae/psycopg_binary-3.3.6-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:79a2a1c3449f6c3409427078ed1cec10de79f3023cb5f2504f0597d350ad46c7", size = 4613633, upload-time = "2026-09-18T13:21:10.664Z" },
    { url = "https://files.pythonhosted.org/packages/d4/47/96225db74be7d2ce04b3a58678b53cda610225055edf5faa775c9f501d8b/psycopg_binary-3.3.6-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:86147cb5d140341c3363fb5bacce31f8d5543902a46699d3c536b101bbceaf9e", size = 4293375, upload-time = "2026-09-18T13:21:16.027Z" },
    { url = "https://files.pythonhosted.org/packages/2a/d2/18e9c779a5efd565250329adaf529ecc2b8b2ed5be5cb0f6ccee208cbfd9/psycopg_binary-3.3.6-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:7308c93cf0b19bbaf8e6ff0a6ad50d3c442385739245fe15a8d593bf841734a6", size = 4019883, upload-time = "2026-09-18T13:21:21.587Z" },
    { url = "https://files.pythonhosted.org/packages/ef/28/0cc654afc6c2cda982767f5679d3646b30b1ec86545bdaa9402202d6776c/psycopg_binary-3.3.6-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:05a83ac9fd52b9bca7cb5ab04b3691163170bd16f53defa27216ea3aa07ee781", size = 4332607, upload-time = "2026-09-18T13:21:27.63Z" },
    { url = "https://files.pythonhosted.org/packages/f1/3e/0a753a74fbd7aef120f286c016e09d3cc3f1daf7688f4a145d27281260b2/psycopg_binary-3.3.6-cp314-cp314-win_amd64.whl", hash = "sha256:1fbd30e537dab22cafdf080608f10148fe2a5f3a61294ddb5113caac8a623840", size = 3755671, upload-time = "2026-09-18T13:21:33.855Z" },
    { url = "https://files.pythonhosted.org/packages/0e/b1/a372b9c02aea50148e71c9853e19efca8fa5ae2010a8e27243b9b8f790c0/psycopg_binary-3.3.6-cp315-cp315-macosx_10_15_x86_64.whl", hash = "sha256:bf8c8481d026b85dd70c5fa7dde85b2333aed0b32a2602bcd38a900cbd78a49c", size = 4719571, upload-time = "2026-09-18T13:21:41.437Z" },
    { url = "https://files.pythonhosted.org/packages/65/7c/811e3828c6b82e2f10c6c9cdd963cfc66f3e024026e5a69ac18530bad984/psycopg_binary-3.3.6-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:b599defe9190b17e9907c8b4d114c181e702c87efcd1b8a0ad40971cdcc4634a", size = 4781230, upload-time = "2026-09-18T13:21:49.516Z" },
    { url = "https://files.pythonhosted.org/packages/3e/15/9a784eed813ea9e97c294af3ead63d02b7b203502c66380336c50065e441/psycopg_binary-3.3.6-cp315-cp315-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:b8ece331509f7a975b90501f41e83ad905e4141753fedf3f2711b2bc70a8efbc", size = 5566111, upload-time = "2026-09-18T13:21:58.089Z" },
    { url = "https://files.pythonhosted.org/packages/68/16/47194e002007c27337b11e49bf459c4b19727463f9aff2e1a90917bcc806/psycopg_binary-3.3.6-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:c61617eaae0112ca154da87ffb99b73af2c74067acac28dfb9a4455b019dff2e", size = 5249963, upload-time = "2026-09-18T13:22:06.695Z" },
    { url = "https://files.pythonhosted.org/packages/53/84/5dcf9f310b11f0675cd860c6b2c70f58ce61798a3ee3f6f962b53fa358ca/psycopg_binary-3.3.6-cp315-cp315-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:c6d19cb4999d03231e8730a5f66c8f5068bc3b532677eb39dab0f600bff3e312", size = 6847925, upload-time = "2026-09-18T13:22:13.088Z" },
    { url = "https://files.pythonhosted.org/packages/f3/06/1957a06dc22963c418c27b284929579de84f29c37ad1abe6dc6ee9e8cf25/psycopg_binary-3.3.6-cp315-cp315-manylinux_2_38_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:e8cbb54454dbf1bbf2ff08dd7693e8d94ac94b1a20f70f4b3b813d52ecb5cbc1", size = 5087720, upload-time = "2026-09-18T13:22:17.959Z" },
    { url = "https://files.pythonhosted.org/packages/21/43/ac07d042bae99b57bf123bb473632f29af544008094da0ffd285ab8011e2/psycopg_binary-3.3.6-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:dc75da5a20951049f7b773145f998f69d181adad9c58a0ff36e0cf1d73c10e10", size = 4613412, upload-time = "2026-09-18T13:22:26.719Z" },
    { url = "https://files.pythonhosted.org/packages/aa/b1/019156fbeafcefb4cccc9d109de4699493bceb8313c7545c8349e089dfbc/psycopg_binary-3.3.6-cp315-cp315-musllinux_1_2_ppc64le.whl", hash = "sha256:955e3dd94da361e052d2e49acf591017158dc8f8ed2c8a42c2e3943403c39dc2", size = 4292618, upload-time = "2026-09-18T13:22:33.042Z" },
    { url = "https://files.pythonhosted.org/packages/5d/0f/62113dc6b1df65983a1f2fc816c04b1edfa22f2ae9d4abee74ed267f4a96/psycopg_binary-3.3.6-cp315-cp315-musllinux_1_2_riscv64.whl", hash = "sha256:c7753871eb57e6a5f4646f6168590c6653073dea5e9e720b201c8875332df4c8", size = 4027121, upload-time = "2026-09-18T13:22:38.334Z" },
    { url = "https://files.pythonhosted.org/packages/5d/d5/cf0cbd1ea5a7d8167fe2c6953efde19101f7b193bd61a23e6d622ad6854c/psycopg_binary-3.3.6-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:303732e798fe6729f8e12021b9c96107df8e95ecec4dd487c67b98ec2a59435e", size = 4336388, upload-time = "2026-09-18T13:22:45.576Z" },
    { url = "https://files.pythonhosted.org/packages/98/33/e2a5b36edf8aa422f6fa4b894756eb33dc93b36df5f65121280bb8b929c4/psycopg_binary-3.3.6-cp315-cp315-win_amd64.whl", hash = "sha256:2f122603f36050937982abf9668d8bc4769a79f7c93a65013b1c49f1cab7b56b", size = 3756154, upload-time = "2026-09-18T13:22:51.283Z" },
]

[[package]]
name = "pydantic"
version = "2.13.5"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "annotated-types" },
    { name = "pydantic-core" },
    { name = "typing-extensions" },
    { name = "typing-inspection" },
]
sdist = { url = "https://files.pythonhosted.org/packages/53/ef/fc4f868f4e2cee79f863883abffceff107875f569b848507319842d2a681/pydantic-2.13.5.tar.gz", hash = "sha256:51a9c5f7b2f8e636f04c6cada605d9b6a3bf1348fdf945a3d8869b19bba0ee08", size = 845750, upload-time = "2026-08-28T14:04:00.916Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/eb/47/c95ffc2009878c7aac0c5e08528022dcb885933252a88b5f170058014464/pydantic-2.13.5-py3-none-any.whl", hash = "sha256:346a034f080da3755d8e9cb5e00e8b07de1d39e4f6e2c87d8ab7cafa0b269a73", size = 472589, upload-time = "2026-08-28T14:03:59.136Z" },
]

[[package]]
name = "pydantic-core"
version = "2.46.5"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/af/f9/8a06bea35ef8daf588f707784c973a7046e0034c8d8cfb08828eeffb8b75/pydantic_core-2.46.5.tar.gz", hash = "sha256:10416c15b8839ecc4ef4d0885da76da6fd0f67333a0eb8aff6d93c4b8f2910fc", size = 472262, upload-time = "2026-08-28T10:01:31.677Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/8e/8a/14596f2a8367da50cf7cbac48169ee5d9c8e11d486a3b527082384630c72/pydantic_core-2.46.5-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:c1c43ad4339643d70ebb8124e1305a7dab423001eff58bb41a0f731adbc98355", size = 2074081, upload-time = "2026-08-28T09:59:16.141Z" },
    { url = "https://files.pythonhosted.org/packages/ae/d5/d8a4eb6d6c7f66b91dd37c576d76e9e60fba900caf5372c17bcf949febc2/pydantic_core-2.46.5-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:1a353f84de772f423b5ffb11d7ae352fbbef0f446f3c0b0af0f8236d7233606e", size = 1920497, upload-time = "2026-08-28T09:59:18.065Z" },
    { url = "https://files.pythonhosted.org/packages/8e/26/092079428f86e927e030b2c0ced87df69dbb1c875cdeaa67bf42ea2be746/pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:5086029a57366b8cf81b130a43908738095c270c21a8d7f0e8bdfdb89718e2f3", size = 1952130, upload-time = "2026-08-28T09:59:20.476Z" },
    { url = "https://files.pythonhosted.org/packages/08/c3/8ec0e290a9ebaebd64047bf5fda94be835c6b1551b02437e4b76778fbcd7/pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:46c25dda9d092a06c08db76ffe0a197107904d0dfac653f7d5306bbcd6d6119c", size = 2026371, upload-time = "2026-08-28T09:59:22.227Z" },
    { url = "https://files.pythonhosted.org/packages/01/72/4fd20ad520fb8da0157f95b27a7eb05a72790ef08138e7701ac972c342ea/pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:37ea7b83c935e5b0d68c9449b82651accf78a10828b2c02b2f2d9e9496446c21", size = 2202822, upload-time = "2026-08-28T09:59:24.277Z" },
    { url = "https://files.pythonhosted.org/packages/31/b0/d16e0771206b29314f0d52198b720be21e8a99ab2bf11e3bc0d7c9cebdff/pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:e64e88d5585bea9ce95861079de72006c7fa6d3df4e3a3b65ba31eb979c15c9f", size = 2262756, upload-time = "2026-08-28T09:59:26.608Z" },
    { url = "https://files.pythonhosted.org/packages/2c/9b/59634b7ac631c63b2a37760eb6943af3e29573d6b59a4abc5e7f019d4cee/pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:54d510bac3ee52247af28ed4bb18a1e799f040ac60fd2bf5ccd4c92f1fbe786f", size = 2068352, upload-time = "2026-08-28T09:59:29.044Z" },
    { url = "https://files.pythonhosted.org/packages/08/7c/570abb1ad2155348dc754ea91be22e5aaa18eb6d69a6068f7c6f2679a6ed/pydantic_core-2.46.5-cp314-cp314-manylinux_2_31_riscv64.whl", hash = "sha256:a2a5e1d0ff29adddc9f6d6821a66302e4493f8ca898b715b6b1182c2c201ea0a", size = 2104777, upload-time = "2026-08-28T09:59:30.95Z" },
    { url = "https://files.pythonhosted.org/packages/8e/25/5bf74adc65a1ac5b7be3f6cb0bcb5433615c1598a801c19d830d84c98ded/pydantic_core-2.46.5-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:03b9666e41e35d8909852ba191a0607520f81b74eaf12ccf8737005dbb313821", size = 2156312, upload-time = "2026-08-28T09:59:32.604Z" },
    { url = "https://files.pythonhosted.org/packages/90/6a/2ef38830675e050121040618135564ed56b860b45433b02d9b4ebece46f3/pydantic_core-2.46.5-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:a91c17edf6eea2402cb5457b4c89e99bc5ed1004aa34c4adf1d4258c1a5c22c2", size = 2150067, upload-time = "2026-08-28T09:59:34.453Z" },
    { url = "https://files.pythonhosted.org/packages/90/ef/a7dbb03a14a64c2a4621f989c615ed9a892535a6cad938fc27079f919d80/pydantic_core-2.46.5-cp314-cp314-musllinux_1_1_armv7l.whl", hash = "sha256:b49924c73a235e969511bf2aabdff3beebf9820931f646c80274d5d780010c47", size = 2304516, upload-time = "2026-08-28T09:59:36.194Z" },
    { url = "https://files.pythonhosted.org/packages/68/f8/6bb4c4b80e8a6fde1904c64a51c62a1d04fcdfa3ea521a66b2ddefa1d885/pydantic_core-2.46.5-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:2cbd9a5eff05e51c447c34dfa4632145b26b09120cf04bd0c871e44c1a5e1c9a", size = 2335223, upload-time = "2026-08-28T09:59:37.931Z" },
    { url = "https://files.pythonhosted.org/packages/2a/80/f46b8c681195190b2c1f1c7c0a81abce60663e987613e09ef64d433dd96b/pydantic_core-2.46.5-cp314-cp314-win32.whl", hash = "sha256:2d5d76654becf5efd62c9e51c3756c67b49498b0c9a40884934c40807adbd074", size = 1934827, upload-time = "2026-08-28T09:59:39.836Z" },
    { url = "https://files.pythonhosted.org/packages/f7/3c/60674207246bc0a4009d2391b7c7251c7159f279c8d2ab8aae8ef46f3dee/pydantic_core-2.46.5-cp314-cp314-win_amd64.whl", hash = "sha256:fa10ef4112775900e7a0661068635eb67b2ab824fbde764de6e0e21982a93db0", size = 2042648, upload-time = "2026-08-28T09:59:41.792Z" },
    { url = "https://files.pythonhosted.org/packages/69/0c/117c562c7c1babdf44576b72a5e496906506c93690387ecfbca7c729ae2e/pydantic_core-2.46.5-cp314-cp314-win_arm64.whl", hash = "sha256:045ab3b6d308439e32b81cc173bba5b9018bc6ed896afd0c65b3b009b1699af5", size = 1989652, upload-time = "2026-08-28T09:59:43.702Z" },
    { url = "https://files.pythonhosted.org/packages/e8/66/9336ae58f9eb68c41d121894e52c4c89eccb07eb8f602a04ee9c3f37736a/pydantic_core-2.46.5-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:8816f3d218beb4b787de5c9759c259b8fa61f9dec42dc7811f320a33771778b7", size = 2065829, upload-time = "2026-08-28T09:59:45.364Z" },
    { url = "https://files.pythonhosted.org/packages/c5/02/bc19b47a96c2d3109760711acf22369e56bd7e405ca52f7ade164d2ead57/pydantic_core-2.46.5-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:bce57638e08ac148e5778cce7feb968307a727d66f8e2274a543d0cf0c9ad6a3", size = 1905716, upload-time = "2026-08-28T09:59:47.18Z" },
    { url = "https://files.pythonhosted.org/packages/52/a4/70b47c0509923dd98ccfed04fb3e32ea3849c82a0ff2205bb41009b43c00/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:976e1128455aa595ea04c79ccfedff1aaeab96ee013fcc916bed120c4f0ad94f", size = 1934216, upload-time = "2026-08-28T09:59:49.241Z" },
    { url = "https://files.pythonhosted.org/packages/52/ab/aa03b65f7bb198585edf806b906c3223ecf1795543e39e23aec4cce27ad2/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e7b891faeedeafba41b2983e5001a81b6a915b69544c7e7570d1989ce1c36ac7", size = 2010635, upload-time = "2026-08-28T09:59:51.692Z" },
    { url = "https://files.pythonhosted.org/packages/3c/8b/0da06343f30b84ec549aafd309c6456223d5dc8bd36af504c573faad561d/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:5f194189415698233dd1114a093a9b56e61e2c57e11b469be3b0506f46f0771c", size = 2209369, upload-time = "2026-08-28T09:59:53.582Z" },
    { url = "https://files.pythonhosted.org/packages/d6/5b/844c4defaa34a3df66eb9257087d121d70c201298b96abdf9f492fc2f1bf/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:82a36973cf8a2ef5406f4fe2edbf8ed0c99629535d959e0b100c76a32535a111", size = 2253238, upload-time = "2026-08-28T09:59:55.484Z" },
    { url = "https://files.pythonhosted.org/packages/f4/64/a4e536cb16d7f61a7fd3120b46c577fc7fa7325992f69c4f52bc786d77d8/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:cdbb78909f52b981d3b2d56b97328d71eb0b974c36bd77c920123a7ebb192829", size = 2065740, upload-time = "2026-08-28T09:59:58.038Z" },
    { url = "https://files.pythonhosted.org/packages/5f/75/aaa38c6bc2d085f6605b34eabdc6a8a4e0b2e61fc9c8e6e52b28e97b3125/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_31_riscv64.whl", hash = "sha256:52e24eacdb536cade636aa90fb851835222becff8484b7001fdc78cb0290f2aa", size = 2087425, upload-time = "2026-08-28T09:59:59.898Z" },
    { url = "https://files.pythonhosted.org/packages/55/ae/fcab4cfc39aba3689e1d20c8b5250ad280957022c09af2ed9cd585602a5e/pydantic_core-2.46.5-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:37ae34309d7bd8c0d61ab839668058f2a7962ea1fc51d105d2db228fe0618034", size = 2139306, upload-time = "2026-08-28T10:00:03.057Z" },
    { url = "https://files.pythonhosted.org/packages/2d/f4/f1d03a4bc9d9acbc62f4d742b8a319af52f71885079868b2ff8e48a651ee/pydantic_core-2.46.5-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:0cdbada856a1c69a7624a64d3d9aefe79300bd6ef827b43a4f265010b9b55184", size = 2144589, upload-time = "2026-08-28T10:00:05.645Z" },
    { url = "https://files.pythonhosted.org/packages/83/f3/7a53bb1356de514a4cd295f25b6ac39237895620c0462d2592b76c16e114/pydantic_core-2.46.5-cp314-cp314t-musllinux_1_1_armv7l.whl", hash = "sha256:545f26c504b27c3758439a5e6d9349931f0a04f855668d5fe323c89e82300a38", size = 2288882, upload-time = "2026-08-28T10:00:07.931Z" },
    { url = "https://files.pythonhosted.org/packages/cd/94/5a81583660c175c59d49ffb09f4b3a44debeaf86a19fca664ae1cdd9ee32/pydantic_core-2.46.5-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:ff218293c9c806138dca139765e3b067621be52bcd93cdc14c7711be7ddc90a9", size = 2335210, upload-time = "2026-08-28T10:00:10.177Z" },
    { url = "https://files.pythonhosted.org/packages/5a/9f/5d685c2693b972d1a59c998586e8823712b66603aeff47ee60a4bdaafd37/pydantic_core-2.46.5-cp314-cp314t-win32.whl", hash = "sha256:97cf3eb53a8cccacf9d46686a0926186c9bfb5574f2ed66d3639d5fe117cd3a9", size = 1921180, upload-time = "2026-08-28T10:00:12.35Z" },
    { url = "https://files.pythonhosted.org/packages/70/12/5c94ee16d65a37a15f9e869f5e6256df111154491173801a4c5e800ab548/pydantic_core-2.46.5-cp314-cp314t-win_amd64.whl", hash = "sha256:d2f9fc07a8042a8f95925b35c4f04f469707c981fc33245b6ca187cf5d2dd290", size = 2020515, upload-time = "2026-08-28T10:00:14.774Z" },
    { url = "https://files.pythonhosted.org/packages/63/19/67830dda664e6bdf9285ee2e40f355d0d7d6b92aa0c42e8d217bb8d33d36/pydantic_core-2.46.5-cp314-cp314t-win_arm64.whl", hash = "sha256:acf8a67ba51f4ca9ddbd0e6b3000a65ac51ab734661778b3e7ba64d99a710f2f", size = 1989276, upload-time = "2026-08-28T10:00:16.984Z" },
]

[[package]]
name = "sqlalchemy"
version = "2.1.5"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/08/bb/28e3106ee586e5b2f5ecf211eec1348055f0f926314b13fe23b9cffa9039/sqlalchemy-2.1.5.tar.gz", hash = "sha256:0df76cf1ca680ad745bd378a6299a058611a8a784eeaeb4ed78ad4a0b7ce2003", size = 10569593, upload-time = "2026-10-16T20:52:20.57Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/01/b0/59b26375cd618e861a9295d855b866ca85be654d20ed47e494e33c3bf26e/sqlalchemy-2.1.5-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:5541a110ac4bb6377c785aea1b8f0b4d6658ed0ca5061ed1115d0725062b026b", size = 2468925, upload-time = "2026-10-16T22:42:40.547Z" },
    { url = "https://files.pythonhosted.org/packages/9e/a1/01931ba38770f169ce70e4034b0dcf2c1a776fe7d8dde93a34b6355510b1/sqlalchemy-2.1.5-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:f029b2f7114623c03f762596f313515a2358004c44eb18924a15940f2e27d30f", size = 4593220, upload-time = "2026-10-16T22:55:29.253Z" },
    { url = "https://files.pythonhosted.org/packages/42/9e/fa478482503a69dfb3b0cb82f3f80fe3816026530dd34b5359e2acd9f30d/sqlalchemy-2.1.5-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:cc44dcc80e89a006af415edffc7409b1f2976a4597065449c166987f95801ab4", size = 4622806, upload-time = "2026-10-16T22:59:27.153Z" },
    { url = "https://files.pythonhosted.org/packages/fc/01/357ff85423013de8316316752c36a6bd1b7f3830c30dc63754afe06ba589/sqlalchemy-2.1.5-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:72ddd7a8ec187d02de0ef316a15aaf381ddcc594958247b02a3dcdb4c42f0b02", size = 4316247, upload-time = "2026-10-16T23:15:14.27Z" },
    { url = "https://files.pythonhosted.org/packages/43/53/88c5af325c81c929d0ed5b7ec15b087173bd3587d93366c5e336b9647267/sqlalchemy-2.1.5-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:f5173a6e60a15090f9e2348a8ca94cc13de72796c16733f3b62fbb22acba07b8", size = 4522522, upload-time = "2026-10-16T22:55:30.835Z" },
    { url = "https://files.pythonhosted.org/packages/87/29/f6f01f121d5e590c568f405f78b8eb3edace446c114126fc428536446dd6/sqlalchemy-2.1.5-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:09b10bd68223d57cce39c08947efae3f91ac40b552e07c7c869c3350a0fc4c23", size = 4317593, upload-time = "2026-10-16T23:15:16.397Z" },
    { url = "https://files.pythonhosted.org/packages/0c/6f/14863fc9aea433645851330242823b1879cdaac71c118f7c9366e7caf4da/sqlalchemy-2.1.5-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:ea4cb5022462d9f15e7b72a52c267385aa97ac224c8503ac63ba90c0067ad0d9", size = 4583207, upload-time = "2026-10-16T22:59:29.322Z" },
    { url = "https://files.pythonhosted.org/packages/a2/e9/6907fc009d9d06e8d03d6bf286df46e878ea2a85c839dcb65ef11ceb3a39/sqlalchemy-2.1.5-cp314-cp314-win32.whl", hash = "sha256:c3ffbe6c680c626403b7e9697d92465501078731b9e8863b1410826e66b950e1", size = 2386018, upload-time = "2026-10-16T22:48:40.692Z" },
    { url = "https://files.pythonhosted.org/packages/e1/d6/dea47b4b361c427d390edc10d73050e6d11d905c56ef26861ff5f94aa8fa/sqlalchemy-2.1.5-cp314-cp314-win_amd64.whl", hash = "sha256:061d089901319463a1160e4596191e355d2a9b4cce4852dac5adc301b085ac2f", size = 2436983, upload-time = "2026-10-16T22:48:42.2Z" },
    { url = "https://files.pythonhosted.org/packages/be/28/305a91768a1ca0980c6ead455dcda5a2c1e616022901898e966ccf913ba9/sqlalchemy-2.1.5-cp314-cp314-win_arm64.whl", hash = "sha256:f5bc7fb93f1c17efefeb062bc4d2742ad1b71d56c36e6e2898a371ac6a56839a", size = 2401394, upload-time = "2026-10-16T22:31:45.275Z" },
    { url = "https://files.pythonhosted.org/packages/5f/6d/d4bab269d94ed1017950873643b5bd3eb271a5b8d5b0451250f0173f90fc/sqlalchemy-2.1.5-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:9bb993b1d0890a2da90589684c3d09de75df82c06aa8f7eda246c7cd0ea3e820", size = 2508315, upload-time = "2026-10-16T22:55:01.45Z" },
    { url = "https://files.pythonhosted.org/packages/d9/80/aeab72b51fceb71b1e1d62cabc6f51c9d8f20588165aa54e0d0d6cc77c05/sqlalchemy-2.1.5-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:df7e71ed051e4003e73484ef6547aacfb3a2322aac0c230d530c97e48e77b4d7", size = 4924848, upload-time = "2026-10-16T22:41:10.671Z" },
    { url = "https://files.pythonhosted.org/packages/05/8b/7318ca0ae828fa1605dd4481f8eeecb5325a7ead6289c1206fb1ff1e2e1d/sqlalchemy-2.1.5-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c76d4cb9c76a6906563133449a76d9eae6c8529ca09484b8615ca604442b442e", size = 4835557, upload-time = "2026-10-16T23:06:18.482Z" },
    { url = "https://files.pythonhosted.org/packages/35/17/7a5a196b0af72d65cbcd3a6fb7c4128693d039faf58a682ffe2d19329420/sqlalchemy-2.1.5-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:59a56be2e4e972061f9d5c1d5b01763b8b2207b48b956fbb6879c7443f5817f7", size = 4513707, upload-time = "2026-10-16T23:28:18.969Z" },
    { url = "https://files.pythonhosted.org/packages/91/50/ca323ed15fc06c73a7fd85a3a339749994c560c12312ee8a53abf0f9a7ec/sqlalchemy-2.1.5-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:bc1a61d7f42e71746b5a2e10e90a6b174b4add441b7b6cf14278f1e029b2b800", size = 4781127, upload-time = "2026-10-16T22:41:12.784Z" },
    { url = "https://files.pythonhosted.org/packages/26/3d/c56a75d0a2f6af08f6bb28d0b69e129911a2fc52b24dbafd7a7e5ac5c1aa/sqlalchemy-2.1.5-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:740e96dfb99a615c8056070d3747efe8bce4c145e5953ccc9e4b004c139de0d2", size = 4513816, upload-time = "2026-10-16T23:28:21.378Z" },
    { url = "https://files.pythonhosted.org/packages/7d/dd/84e0cd627bbd3e35b5f033191a4f597e611ff96e424db36a444a8d6755cc/sqlalchemy-2.1.5-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:92a0bb0595331c8e40bc615a67cc7bca9b761487409d1bf46c598b6ba5c0754d", size = 4772462, upload-time = "2026-10-16T23:06:20.876Z" },
    { url = "https://files.pythonhosted.org/packages/b7/47/cf0a920fc40344f8a1806d661e7c702341aebd871e31e1d1d6e0fbc9d1e0/sqlalchemy-2.1.5-cp314-cp314t-win32.whl", hash = "sha256:11185c72b5372369166cb721537943f8e1e6e42a399e9bac19e02f3ee20592a4", size = 2444861, upload-time = "2026-10-16T22:51:51.169Z" },
    { url = "https://files.pythonhosted.org/packages/bc/1d/4c5dc7e30fe740a01df4ba5ab800be2d7674b87f042e4c21c7ca89b36f9d/sqlalchemy-2.1.5-cp314-cp314t-win_amd64.whl", hash = "sha256:5173207b8fe1ddfc1d451c420a2a9cbbd0734b4a19896b8080e3744497e1c20c", size = 2512497, upload-time = "2026-10-16T22:51:53.014Z" },
    { url = "https://files.pythonhosted.org/packages/5f/2f/d3e9bfb1faabea302b98ba8c9dd6252bc362c6afeabe28ffcc1eea8a6bd2/sqlalchemy-2.1.5-cp314-cp314t-win_arm64.whl", hash = "sha256:def2f117a6ec0a25202ee36a148bbcfad3d43e2f2bb2e698e6d4448c6db5cb19", size = 2430598, upload-time = "2026-10-16T22:32:54.554Z" },
    { url = "https://files.pythonhosted.org/packages/ad/7c/17f07378eea7ec2fac8ac60f99fe3c474ef5c19a3adede70ae9886eb82d7/sqlalchemy-2.1.5-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:a0b80f91d9ed92be7a134278ea2e83a693c07d9986824ca51d859af9e57e18f5", size = 2468856, upload-time = "2026-10-16T22:27:43.754Z" },
    { url = "https://files.pythonhosted.org/packages/7f/c0/4fef29827b198937e09c40d0fa36b9738bd3914f0e5040927dfac8dfee21/sqlalchemy-2.1.5-cp315-cp315-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:3033ddeeeb34c6c536622c07e932a20f8c9f58d6dd76e56595a76b55a25011ff", size = 4597018, upload-time = "2026-10-16T22:41:59.749Z" },
    { url = "https://files.pythonhosted.org/packages/eb/d8/37645f8445ac3774e18f8dc72e0fa0ac868e0dff0e987ff3bec644f55102/sqlalchemy-2.1.5-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:f4d30723171d511ec16ac057872a38b9b395420c0aaf81b2f94dd7bf1345c5fe", size = 4632322, upload-time = "2026-10-16T22:44:53.83Z" },
    { url = "https://files.pythonhosted.org/packages/c2/c9/15466cd08a6c329acc4f730dff7041e84122456fe38c518c93a07d6d82ca/sqlalchemy-2.1.5-cp315-cp315-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:5cefa5badc13df1c9082bacdfa435c8eb6dcb9b32717f51d09d1e160a599646f", size = 4338381, upload-time = "2026-10-16T23:01:22.714Z" },
    { url = "https://files.pythonhosted.org/packages/12/2b/a93b7c8f6886138dac91f66fccd3b42473c365408d9a4c1b69403cf206f8/sqlalchemy-2.1.5-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:2549e503185897de1fc5ca7730d5daed0d27d0b26df4a059dcdd33ebe81b7b4b", size = 4525244, upload-time = "2026-10-16T22:42:01.631Z" },
    { url = "https://files.pythonhosted.org/packages/b3/47/d3926cacd194be073a2053a05470f20ed7da623f399e95213c1e497954fd/sqlalchemy-2.1.5-cp315-cp315-musllinux_1_2_riscv64.whl", hash = "sha256:5a6871ee159a943d874012de835d56d0544ee871a99dbae05bc053da315b2c23", size = 4337223, upload-time = "2026-10-16T23:01:24.702Z" },
    { url = "https://files.pythonhosted.org/packages/ea/a8/b15ab4712342a18fb3949c77687c24d3749e86079c9905cc2cbebbd44da3/sqlalchemy-2.1.5-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:51e290080415325b66a94d20f6360e310606acb832f2bd677d4fcb95728e7ce1", size = 4594562, upload-time = "2026-10-16T22:44:55.661Z" },
    { url = "https://files.pythonhosted.org/packages/9a/ab/3b6ef6c77740d7fbf5a3eb45f95768fb809b0769bd21df81d5f8c002e5a5/sqlalchemy-2.1.5-cp315-cp315-win32.whl", hash = "sha256:c228084025a28aa038aef9b821d842508650fe12fe51f06e9cdaa4393be7812c", size = 2385770, upload-time = "2026-10-16T22:41:04.484Z" },
    { url = "https://files.pythonhosted.org/packages/4b/c1/0b3256bc11487b2846a26d58946caea0ed395fd500951a16fb82d31a20ff/sqlalchemy-2.1.5-cp315-cp315-win_amd64.whl", hash = "sha256:bc09dd22c3fc491a2df7d16ca4167de35573f40c2e82dd4d6ddae589a73e7032", size = 2437043, upload-time = "2026-10-16T22:41:06.12Z" },
    { url = "https://files.pythonhosted.org/packages/e5/a0/09eaa7897f6f745de16220b20c63660948a95716be90d2f405af08222e57/sqlalchemy-2.1.5-cp315-cp315-win_arm64.whl", hash = "sha256:375ef1bf78bc269a220963163d2580d5377898ed23a00bdd98a02d755421573d", size = 2401090, upload-time = "2026-10-16T22:28:58.035Z" },
    { url = "https://files.pythonhosted.org/packages/c2/c2/4c747dcc6fe329dd07ab57233f334eca19a3ff05934e0aba4f25a0977a67/sqlalchemy-2.1.5-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:7af1c92255cf8d50e87a808ce41096907332acdd09f285426a52f7c300e152db", size = 2504475, upload-time = "2026-10-16T22:55:02.946Z" },
    { url = "https://files.pythonhosted.org/packages/07/f1/183446b1bc29484087ba7a6bb199a265c0559bf8ff201c1ee54bf1fe0936/sqlalchemy-2.1.5-cp315-cp315t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:85891e0828e76a77fe912995dbc3ee949099488ba0a2ab323535d2e767446b20", size = 4902197, upload-time = "2026-10-16T22:41:14.703Z" },
    { url = "https://files.pythonhosted.org/packages/31/0b/b24baf343461eefdecc672df1ccbb14c8c64028a11625dabc97b0bb9791b/sqlalchemy-2.1.5-cp315-cp315t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:a72e062d2d38826dd89231df692fb40f12d7d1b9d118be23bcc1cf93c6e31782", size = 4851871, upload-time = "2026-10-16T23:06:22.861Z" },
    { url = "https://files.pythonhosted.org/packages/da/27/f688b34ea3d85b38e01b7463874f1f4b91619dfed4e6cac88c27caface73/sqlalchemy-2.1.5-cp315-cp315t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:b79ee943e2e12246f873345762b83dbadd1fcfc3e832eab83272d672704dbdea", size = 4500095, upload-time = "2026-10-16T23:28:23.431Z" },
    { url = "https://files.pythonhosted.org/packages/b2/04/d8e13be8d0c25ba49244a9c24579ef61d5a6b57f98e55fbb173b7923ec3a/sqlalchemy-2.1.5-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:e9418d87b55c469c2f1328246d4533238cdc43134c695d6b9a6b7a87da49d463", size = 4757826, upload-time = "2026-10-16T22:41:16.465Z" },
    { url = "https://files.pythonhosted.org/packages/86/2e/a0bd2ead949cc605ce3ad5d38e2fe84963b2aa7f89e8648c1bbad13a3679/sqlalchemy-2.1.5-cp315-cp315t-musllinux_1_2_riscv64.whl", hash = "sha256:898d86c22640fe52ffe02b4abc043a3c6754b4875837599e739be440966dffa1", size = 4499377, upload-time = "2026-10-16T23:28:25.203Z" },
    { url = "https://files.pythonhosted.org/packages/b9/dd/c1ca0713a1a7d8d6eb5864edd2d11d7a6a327aaba664645733cb53662425/sqlalchemy-2.1.5-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:b3ad20cd035392f2b91a6466e24643990c1378beda80c9bda87a3a41e841e838", size = 4777264, upload-time = "2026-10-16T23:06:25.203Z" },
    { url = "https://files.pythonhosted.org/packages/5a/dc/9dec72cea689f16bc8ecfcd62b4aa2796009a7cef6be85a9f70310ecf71b/sqlalchemy-2.1.5-cp315-cp315t-win32.whl", hash = "sha256:db34eefaf992c84460ab26ecf2fc2bdcc68965d6becfae8182cae0efeaa3e8f8", size = 2441666, upload-time = "2026-10-16T22:51:54.58Z" },
    { url = "https://files.pythonhosted.org/packages/dc/28/f44c4524ce8a68935bd6f23ee801165072fb8c1e477fc9855efd9eaa2360/sqlalchemy-2.1.5-cp315-cp315t-win_amd64.whl", hash = "sha256:173054351d863ddada188284e309e87a9f030132c8d534e05458971ff061aa1e", size = 2507526, upload-time = "2026-10-16T22:51:56.262Z" },
    { url = "https://files.pythonhosted.org/packages/b1/fc/e90c91f6c2709a431f9b75e41bd31216337859411359f4a4fc2615c989e3/sqlalchemy-2.1.5-cp315-cp315t-win_arm64.whl", hash = "sha256:22c8d0873168a54f614e381559ea83d547b2cc5488b95b049bdc92667586bd5f", size = 2426204, upload-time = "2026-10-16T22:32:56.011Z" },
    { url = "https://files.pythonhosted.org/packages/de/e9/61176e4753f74ab5f6e72a56314ee654d25c31e6fc98c99060442998cccb/sqlalchemy-2.1.5-py3-none-any.whl", hash = "sha256:2f77b77b716f005b2dc3cc059d56df6a919bfb5b439e4149890a9df6c36be9e3", size = 2060214, upload-time = "2026-10-16T22:43:30.801Z" },
]

[[package]]
name = "starlette"
version = "1.6.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "anyio" },
]
sdist = { url = "https://files.pythonhosted.org/packages/b5/b4/205b0d5241d934e8add0c38aa924c4f9fb7330834ff11e5444db964ec3f9/starlette-1.6.0.tar.gz", hash = "sha256:d4e3ac5e546444960c710297a3c9fc3f7ebae1b7e963f3d36173b49da535be9b", size = 2716969, upload-time = "2026-08-08T18:27:57.512Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c8/cb/6a6a47d5b464bd08695d254f3da6e7986cc70c9fa5d778eda57538edfe56/starlette-1.6.0-py3-none-any.whl", hash = "sha256:a86dd39d14bb45f85a3d18525215a9ef0cfd1f192ac793220e72598c90335f0c", size = 75969, upload-time = "2026-08-08T18:27:56.196Z" },
]

[[package]]
name = "typing-extensions"
version = "4.16.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f6/cc/6253133b5bb138fc3306cebfbda2c520f545d36b5be2c7255cc528bb45d6/typing_extensions-4.16.0.tar.gz", hash = "sha256:dc983d19a509c94dba722ee6abd33940f7c05a89e243c47e907eb4db6f1a43e5", size = 113555, upload-time = "2026-07-02T08:40:05.92Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl", hash = "sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8", size = 45571, upload-time = "2026-07-02T08:40:04.659Z" },
]

[[package]]
name = "typing-inspection"
version = "0.4.4"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/a3/26/b09b8010994eccc3c09092e6b34058f36a460eea2d4c3e8b910c695975a0/typing_inspection-0.4.4.tar.gz", hash = "sha256:547274fa6b0a561ccf549cc9524b999a578e737d015d8709d021f9d0d13bea47", size = 76928, upload-time = "2026-08-12T12:37:25.997Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/67/81/4add07e5172b7ac40d8ed5ff580409a7801a4fe26d529bdd915401dabfbe/typing_inspection-0.4.4-py3-none-any.whl", hash = "sha256:65b8397ba37ccbce054456aaccddfc91e6e3083c92824df348d96ca832f3f147", size = 14750, upload-time = "2026-08-12T12:37:24.648Z" },
]

[[package]]
name = "tzdata"
version = "2026.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/7a/29/6a1391d31cd00ff9e927215a224a880e1e84e826b64ba80a499e51c074d8/tzdata-2026.6.tar.gz", hash = "sha256:85d2cd9c09f81f0bb29db27759fc83af4f1e620efb814f8c5bf8b4cc4feece6d", size = 201017, upload-time = "2026-10-28T09:57:09.137Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/0a/66/9a06c2227fedfd4919f0eaaa8b94377d9730882a7e4f95823c9a331ab5e1/tzdata-2026.6-py2.py3-none-any.whl", hash = "sha256:0a10eec6e13ef16b627fabed9a5f2ba61a62b1c67f327305f4e7e412a70b4aec", size = 348210, upload-time = "2026-10-28T09:57:07.276Z" },
]

[[package]]
name = "uvicorn"
version = "0.52.4"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
    { name = "h11" },
]
sdist = { url = "https://files.pythonhosted.org/packages/f2/0f/3f86e61397dd33bf2ccf28188c40db6a740658aeebbbf6e7dbc101a1f487/uvicorn-0.52.4.tar.gz", hash = "sha256:73acfee47a0b133c5de13d219492d62d8a31e935f4fe6e41a232451a15379f86", size = 100627, upload-time = "2026-08-19T06:27:41.821Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f1/79/4a20b54ab0491485ccd8c077db2d39187c7f12b3e15485d38a7be37c81b4/uvicorn-0.52.4-py3-none-any.whl", hash = "sha256:f86e41a149d7d05a9969337e3946a9c171c06a5d42680896daaba624aeac8da1", size = 79871, upload-time = "2026-08-19T06:27:40.36Z" },
]
```

## 5. Configuración, variables y despliegue

| Variable | Propósito |
| --- | --- |
| POSTGRES_USER | Usuario Postgres de Compose |
| POSTGRES_PASSWORD | Contraseña Postgres |
| POSTGRES_DB | Nombre de BD |
| DATABASE_URL | URL de conexión SQLAlchemy |

Copiar .env.example a .env y completar localmente. No subir secretos. La app no carga .env automáticamente fuera de Compose.

### Instalación local

```bash
uv sync
export DATABASE_URL="sqlite:///./minimarket.db"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

PowerShell: $env:DATABASE_URL="sqlite:///./minimarket.db".

### Docker Compose y datos demo

```bash
cp .env.example .env
docker compose up --build
uv run python -m app.repositories.seeder.seed_todos
```

Compose inicia PostgreSQL 16, API y Adminer; aplica migración y luego Uvicorn. Puertos host: API 8001, Postgres 5432, Adminer 8080. Volumen persistente postgres_data. Pruebas aisladas: bash tests/ejecutar_pruebas.sh (uv, curl, Node/npx).


