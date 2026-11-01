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
POSTGRES_USER=usuariouno
POSTGRES_PASSWORD=secreto4321
POSTGRES_DB=backend_database
```

| Variable | Descripción |
| --- | --- |
| `POSTGRES_USER` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Contraseña del usuario. |
| `POSTGRES_DB` | Nombre de la base de datos. |
| `DATABASE_URL` | Conexión SQLAlchemy. Compose la construye como `postgresql+psycopg://USER:PASS@db:5432/DB`. |

Notas: sin `DATABASE_URL`, `app.base_datos` usa `sqlite:///./minimarket.db`; Alembic sí requiere `DATABASE_URL`; `.env` está en `.gitignore`.

## Base de datos

- **PostgreSQL (Docker):** imagen `postgres:16`, volumen `postgres_data` y healthcheck. Desde el host: `postgresql+psycopg://usuariouno:secreto4321@localhost:5432/backend_database`.
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
