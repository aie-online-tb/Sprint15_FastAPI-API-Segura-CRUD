![Cabecera](./assets/cabecera_thebridge.png)

# API segura + cliente Streamlit

Repo de práctica: una **API FastAPI** con seguridad (API key, rate limit, CORS, paginación) y un **cliente Streamlit** que la consume. Dos carpetas a propósito — backend y front no se mezclan.

```text
cliente (Streamlit :8501) ──HTTP──► API (FastAPI :8000)
         02_cliente_streamlit/         01_api_segura_crud/
```

## Estructura

```text
.
├── README.md                 # Esta guía (arranque unificado)
├── 01_api_segura_crud/       # Servidor: CRUD + seguridad
│   ├── app.py
│   ├── security.py
│   ├── rate_limit.py
│   ├── config.py
│   ├── schemas.py
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md             # Práctica guiada (curl / Swagger / errores)
└── 02_cliente_streamlit/     # Cliente: pide /items por HTTP
    ├── app.py
    ├── requirements.txt
    └── README.md
```

| Carpeta | Rol | Puerto típico |
|---------|-----|----------------|
| [`01_api_segura_crud/`](./01_api_segura_crud/) | Servidor | `8000` (`/docs`) |
| [`02_cliente_streamlit/`](./02_cliente_streamlit/) | Cliente | `8501` |

Cada una tiene su propio `requirements.txt` y su propio `.venv`.

---

## Cómo ejecutarlo

Clonamos el repo y abrimos **dos terminales**.

### Terminal A — API

```bash
cd 01_api_segura_crud
python -m venv .venv
source .venv/bin/activate          # Git Bash / macOS / Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env               # editamos API_KEY
uvicorn app:app --reload --port 8000
```

Comprobación rápida: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status":"ok"}`  
Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (en rutas protegidas, query `api_key` = valor del `.env`).

### Terminal B — Cliente Streamlit

```bash
cd 02_cliente_streamlit
python -m venv .venv
source .venv/bin/activate          # Git Bash / macOS / Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env               # misma API_KEY que el servidor
streamlit run app.py
```

La `API_KEY` va en el **`.env` del cliente** (igual que en el del servidor).  
Sidebar: URL + `limit`. **Listar con clave** → 200. **Sin clave** → 401.

---

## Qué practicamos

1. **Servidor vs cliente:** el `.env` configura la API; quien llama envía `?api_key=...`.
2. **Auth y límites:** 401 sin clave / clave mala; 429 si nos pasamos del rate limit.
3. **Negocio ≠ auth:** con clave válida seguimos viendo 404 / 409 / 422.
4. **Front que consume API:** Streamlit hace `requests.get` → status + cuerpo en pantalla.

Detalle paso a paso (paginación, logs, checklist): [`01_api_segura_crud/README.md`](./01_api_segura_crud/README.md).

**CORS:** el cliente Streamlit llama desde **Python** (`requests`), así que CORS no interviene aquí. CORS importa cuando el **navegador** pide a otro origen; la API ya declara `CORS_ORIGINS` en el `.env` para ese caso.

---

## Orden recomendado

1. Arrancar la API y probar en `/docs` o curl (README de `01_`).
2. Arrancar el cliente y repetir 200 / 401 desde la UI.
