# Luwesin Studio

Aplikasi penulisan ulang teks berbasis AI untuk menghasilkan gaya bahasa natural, luwes, dan mengalir menggunakan model target **Claude Opus 5** via endpoint OpenAI-compatible.

---

## Struktur Proyek

```text
luwesin/
|-- .env.example        # Konfigurasi environment terpusat
|-- docs/
|   \-- architecture.md # Dokumentasi arsitektur sistem & riset AI detection
|-- backend/
|   |-- config.py       # Konfigurasi server backend
|   |-- engine.py       # Analisis teks dan integrasi LLM
|   |-- main.py         # REST API FastAPI (Port 8035)
|   |-- pyproject.toml  # Konfigurasi dependensi uv / pip
|   |-- requirements.txt
|   \-- uv.lock         # Lockfile dependensi backend
\-- frontend/
    |-- src/
    |   |-- components/ # Komponen UI React
    |   |-- hooks/      # State management (useHumanizer)
    |   \-- services/   # REST API client
    |-- vite.config.ts  # Dev server Vite (Port 8085)
    \-- package.json
```

---

## Panduan Menjalankan

### 1. Konfigurasi Environment

Salin file `.env.example` ke `.env` di direktori root:

```bash
cp .env.example .env
```

Sesuaikan nilai variabel pada `.env`:
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8035
CORS_ORIGINS=http://localhost:8085,http://127.0.0.1:8085

FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8085

PROVIDER_URL=https://your-provider-url.com/v1
API_KEY=your_api_key_here
MODEL_NAME=claude-opus-5

REQUEST_TIMEOUT=60.0
MODEL_TEMPERATURE=0.75
```

> **Catatan:** Anda juga dapat memasukkan atau mengubah `PROVIDER_URL` dan `API_KEY` secara langsung melalui tombol **Settings** di antarmuka web.

### 2. Backend (FastAPI - Port 8035)

```bash
cd backend
source .venv/bin/activate
uvicorn main:applicationServer --port 8035 --reload
```

*Atau menggunakan `uv` secara langsung:*
```bash
cd backend
uv sync
uv run uvicorn main:applicationServer --port 8035 --reload
```

*Jika menggunakan `pip` manual:*
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend (React Vite - Port 8085)

```bash
cd frontend
npm install
npm run dev
```

Buka aplikasi di peramban: `http://localhost:8085`

---

## Pengujian (Testing)

Jalankan pengujian backend menggunakan `pytest`:

```bash
cd backend
source .venv/bin/activate
pytest
```
