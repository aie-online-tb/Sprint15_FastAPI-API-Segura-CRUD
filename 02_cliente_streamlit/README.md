![Cabecera](../assets/cabecera_thebridge.png)

# Cliente Streamlit → API segura

**No es el backend.** Solo un cliente HTTP hacia [`../01_api_segura_crud/`](../01_api_segura_crud/).

La guía de arranque (venv API + venv cliente, dos terminales) está en el **[README raíz](../README.md)**.

Atajo si ya tenemos la API en `:8000`:

```bash
python -m venv .venv
source .venv/bin/activate          # Git Bash / macOS / Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env               # misma API_KEY que el servidor
streamlit run app.py
```

La `API_KEY` sale del **`.env` de este cliente** (no del sidebar). Debe coincidir con la del servidor.  
Sidebar: URL (o `API_BASE_URL` del `.env`) + `limit`.

Botones: **Listar con clave** → 200; **sin clave** → 401.
