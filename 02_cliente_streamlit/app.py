"""
Cliente mínimo (Streamlit) → llama a la API FastAPI segura que hemos creado.

Idea: el front NO es la API. Aquí solo hacemos HTTP GET y mostramos
el status + el cuerpo. La API key viaja en la query (?api_key=...).
La clave se lee del .env de ESTE cliente (no se teclea en el sidebar).

Arranque: ver README (venv propio + streamlit run app.py; API en :8000).
"""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # .env junto a este app.py (API_KEY, API_BASE_URL)

# Misma clave que API_KEY del servidor; el cliente la envía en ?api_key=
api_key = (os.getenv("API_KEY") or "").strip()
default_base = (os.getenv("API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Cliente → API segura", layout="centered")
st.title("Cliente Streamlit → API `/items`")
st.caption(
    "Demo corta: un proceso cliente pide datos a otro proceso servidor. "
    "La clave vive en el `.env` de este cliente (solo local)."
)

with st.sidebar:
    st.header("Conexión")
    if api_key:
        st.success("API_KEY cargada desde `.env`")
    else:
        st.warning("Falta API_KEY en `.env` (copiad `.env.example`).")
    base_url = st.text_input(
        "URL base de la API",
        value=default_base,
        help="Donde corre uvicorn (carpeta 01_api_segura_crud). Por defecto: API_BASE_URL del .env.",
    ).rstrip("/")
    limit = st.number_input("limit", min_value=1, max_value=100, value=3)

st.markdown(
    """
**Flujo:** Streamlit (este proceso) → `requests.get(...)` → FastAPI (`:8000`).

Nota: como la petición sale de **Python** (no del navegador hacia la API),
aquí **no entra CORS**. CORS importa cuando el JS del navegador llama a otro origen.
"""
)

col1, col2 = st.columns(2)


def _get_items(*, with_key: bool) -> None:
    """Una sola petición GET /items; mostramos status y cuerpo."""
    url = f"{base_url}/items"
    params: dict = {"limit": int(limit)}
    if with_key and api_key:
        params["api_key"] = api_key

    # No mostramos api_key (secreto)
    auth_nota = "con api_key" if with_key else "sin api_key (esperamos 401)"
    st.code(
        f"GET /items  ({auth_nota})\nlimit: {int(limit)}",
        language="text",
    )

    try:
        r = requests.get(url, params=params, timeout=10)
    except requests.RequestException as exc:
        st.error(f"No pudimos conectar con la API: {exc}")
        st.info(
            "¿Está uvicorn en marcha? "
            "Desde `01_api_segura_crud/`: `uvicorn app:app --reload --port 8000`"
        )
        return

    st.metric("Status HTTP", r.status_code)

    if r.status_code == 200:
        data = r.json()
        st.success("200 — listado OK")
        st.dataframe(data, use_container_width=True)
    elif r.status_code == 401:
        st.warning("401 — falta api_key o no coincide con el .env del servidor")
        st.json(r.json())
    else:
        st.error(f"Respuesta {r.status_code}")
        try:
            st.json(r.json())
        except ValueError:
            st.text(r.text)


with col1:
    if st.button("Listar ítems (con clave)", type="primary", use_container_width=True):
        if not api_key:
            st.warning("Falta API_KEY en el `.env` de este cliente (misma que la del servidor).")
        else:
            _get_items(with_key=True)

with col2:
    if st.button("Listar sin clave → 401", use_container_width=True):
        _get_items(with_key=False)
