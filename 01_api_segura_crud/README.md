![Cabecera](../../../../../06_AI_Agents_Engineering/Sprint_11/assets/cabecera_thebridge.png)

# Workout — API segura (CRUD + API key)

**La API ya está dada:** un CRUD de ítems en memoria (`/items`, Pydantic, Swagger). No tenemos que diseñarla desde cero.

**Qué hacemos ahora:** meterle **seguridad y robustez** — API key por query, rate limit, **CORS**, errores claros — y aprovechar el listado para ver **paginación** (`skip` / `limit`).

```text
cliente → /items?api_key=... → rate limit → CRUD
                ↓
        /health y /docs sin clave
```

### Cómo funciona la clave (servidor vs cliente)

1. **En el servidor** guardamos la clave válida en `.env` (`API_KEY=...`). La app la lee al arrancar.
2. **Quien haga una petición** a las rutas protegidas debe enviar `api_key` en la query (`?api_key=...`).
3. Esa `api_key` **debe coincidir** con la del `.env`. Si falta o no coincide → **401**.

El `.env` no viaja con la petición: solo configura nuestro proceso. El cliente necesita conocer la misma clave para poder hacer peticiones a las rutas protegidas.

**Varias claves (idea, no en este workout):** en producción suele haber **más de un cliente** (alumno, profe, otro servicio…), cada uno con su `api_key`. El servidor aceptaría una **lista** de claves válidas; el rate limit de este proyecto **ya cuenta por clave** (`rate_limit.py`), así que cada cliente tendría su propio cupo. Aquí usamos **una sola** `API_KEY` para no complicar la práctica.

### Autenticación con API key

Usamos **API key** porque esta API se llama desde **otro cliente o servicio** (Swagger, scripts, otra app): una clave en `.env` basta para cerrar las rutas sensibles, sin login ni front.

La enviamos como **query param** (`?api_key=...`), patrón habitual en muchas APIs públicas/demo.

### Uso de CORS

Si un **navegador** llama a nuestra API desde **otro origen** (otro puerto o dominio — p. ej. front en `:3000` o Streamlit en `:8501`), el navegador exige que la API declare que ese origen está permitido. Eso es **CORS**.

- Lo configuramos con `CORSMiddleware` en `app.py`.
- Los orígenes viven en **`.env`** (`CORS_ORIGINS=...`), porque **cambian según el entorno** (local, staging, producción). No hardcodeamos solo un dominio en el código.
- Con `/docs` en el mismo host a veces “no se nota”; igual conviene dejarlo puesto: el día que haya un front aparte, la API ya está preparada.

---

## Estructura

```text
.
├── app.py             # Rutas + /health + CRUD + CORS
├── schemas.py         # Item (Pydantic) — API dada
├── config.py          # API_KEY, rate limit, CORS_ORIGINS
├── security.py        # require_api_key (?api_key=)
├── rate_limit.py      # Contador en memoria → 429
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Instalación y arranque

```bash
python -m venv .venv
source .venv/bin/activate          # Git Bash / macOS / Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env               # editamos API_KEY
uvicorn app:app --reload --port 8000
```

**http://127.0.0.1:8000/docs**

En Swagger, en cada ruta protegida: *Try it out* → rellenamos el query **`api_key`** con el valor de nuestro `.env`.

---

## Rutas

| Método | Ruta | ¿Clave? | Qué hace |
|--------|------|---------|----------|
| GET | `/health` | No | Pulso |
| GET | `/docs` | No | Swagger |
| GET/POST/PUT/DELETE | `/items…` | **Sí** (`?api_key=`) | CRUD (API dada; listado con `skip`/`limit`) |

### Paginación simple en `GET /items`

Hay **8 ítems** de ejemplo en memoria. El listado acepta query params:

| Param | Qué hace | Default |
|-------|----------|---------|
| `skip` | Cuántos ítems **saltar** desde el inicio | `0` |
| `limit` | Cuántos ítems **devolver** como máximo (1–100) | `10` |
| `on_offer` | Si lo enviamos, filtrar por oferta (`true` / `false`) | (sin filtro) |

No es “página 1 / página 2” con metadatos: es un **offset** típico en APIs REST (`lista[skip : skip+limit]`). Así el cliente pide trozos sin traer todo el catálogo de golpe.

También podemos combinarlos con `api_key`, p. ej.  
`/items?api_key=<CLAVE>&skip=0&limit=3`.

---

## Práctica guiada

Sustituimos `<CLAVE>` por el valor de `API_KEY` en nuestro `.env`.

### 1) Health sin clave

GET `http://127.0.0.1:8000/health` → **200** `{"status":"ok"}`.

### 2) Items sin API KEY → 401

GET `http://127.0.0.1:8000/items` → **401**.

### 3) Items con API KEY → 200

GET `http://127.0.0.1:8000/items?api_key=<CLAVE>` → lista de **8** ítems (el `limit` por defecto es 10).

### 4) Paginación con `skip` y `limit`

GET `http://127.0.0.1:8000/items?api_key=<CLAVE>&skip=0&limit=3`  
→ los **3 primeros** (ids 1–3: Laptop, Smartphone, Auriculares).

GET `http://127.0.0.1:8000/items?api_key=<CLAVE>&skip=3&limit=3`  
→ el **siguiente trozo** (ids 4–6: Teclado, Ratón, Monitor).

GET `http://127.0.0.1:8000/items?api_key=<CLAVE>&skip=6&limit=3`  
→ el **resto** (ids 7–8: Webcam, Dock).

(Opcional) GET `...?api_key=<CLAVE>&on_offer=true` → solo ítems en oferta.

### 5) API KEY incorrecta → 401

GET `http://127.0.0.1:8000/items?api_key=incorrecta` → **401**.

Miramos también la **consola** de `uvicorn`: debería salir un `WARNING` tipo `auth 401: api_key ausente o inválida` (sin imprimir la clave).

### 6) Rate limit → 429

Con `RATE_LIMIT_PER_MINUTE=10` en `.env`, repetimos GET `/items?api_key=<CLAVE>` **más de 10 veces** en menos de un minuto → **429**.

En consola: `WARNING` con `rate limit 429: ...`.

(Reiniciamos `uvicorn` para resetear el contador en RAM.)

### 7) Sin `API_KEY` en el servidor → 503

(Opcional) Comentamos/vaciamos `API_KEY` en `.env`, reiniciamos, llamamos `/items?api_key=lo-que-sea` → **503**.

En consola: `ERROR` con `auth 503: API_KEY no configurada...`.

### 8) Errores de negocio **con** API key

La clave no “omite” la lógica de la API: primero se comprueba `api_key`; si es válida, siguen aplicando **404 / 409 / 422**.

Usamos siempre `?api_key=<CLAVE>` (o el campo `api_key` en Swagger).

**404 — no existe**

GET `http://127.0.0.1:8000/items/99?api_key=<CLAVE>` → **404** (`Ítem no encontrado`).

**409 — id duplicado**

POST `http://127.0.0.1:8000/items?api_key=<CLAVE>` con body (id que ya existe, p. ej. `1`):

```json
{
  "id": 1,
  "name": "Otro",
  "description": "Duplicado",
  "price": 10.0,
  "on_offer": false
}
```

→ **409** (`Ya existe un ítem con ese id`).

**422 — body inválido (Pydantic)**

POST con `price` negativo (o `name: ""`):

```json
{
  "id": 99,
  "name": "Roto",
  "description": "Mal precio",
  "price": -1,
  "on_offer": false
}
```

→ **422** (validación automática; no hace falta un `if` manual).

**Contraste auth vs negocio**

El mismo POST **sin** `api_key` → **401** (ni siquiera llegamos al 409/422).  
Con clave mala → **401**. Con clave buena + datos malos / id inexistente → **422** / **404** / **409**.

---

## Cómo leer el código

1. **`schemas.py` / rutas `/items`** — la API de negocio (ya dada).
2. **`config.py`** — qué sale del `.env` (`API_KEY`, rate limit, `CORS_ORIGINS`).
3. **`security.py`** + **`rate_limit.py`** — 401 / 429 / 503 (`?api_key=`) y logs `WARNING`/`ERROR` en consola.
4. **`app.py`** — `CORSMiddleware` + `dependencies=[Depends(require_api_key)]` en rutas sensibles.

Idea: **API de negocio dada; capa de protección alrededor**. El cliente ve el status; nosotros vemos el detalle en logs (puente a observabilidad).

---

## Qué NO hace

- Login de usuarios (el cliente Streamlit es carpeta hermana, solo consume la API).
- Rate limit distribuido (Redis, etc.): el contador vive en RAM del proceso.
- Timeouts simulados (eso tiene más sentido con un LLM / agente, más adelante).
- Docker / despliegue en la nube.

---

## Checklist

- [ ] `/health` sin clave OK.
- [ ] `/items` sin `api_key` → 401; con `?api_key=` → 200 (8 ítems).
- [ ] Probamos `skip` / `limit` (varios trozos del listado).
- [ ] Forzamos un **429** y vimos el `WARNING` en consola.
- [ ] Forzamos un **401** y vimos el log de auth (sin secretos en el mensaje).
- [ ] Con `api_key` válida: forzamos **404**, **409** y **422** (negocio ≠ auth).
- [ ] Sabemos qué es CORS y por qué `CORS_ORIGINS` va en el `.env` (el dominio puede cambiar).
- [ ] Entendemos por qué usamos API key (y por query) en este tipo de API.
