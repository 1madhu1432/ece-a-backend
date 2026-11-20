# ECE AI Studio - Backend & Execution Engine

Production-grade FastAPI backend and scientific execution sandbox for **ECE AI Studio**, an engineering simulation platform for Electronics and Communication Engineering students.

## 🚀 Key Modules

- **FastAPI Core (`backend/app/`)**: REST APIs, JWT authentication with bcrypt, SQLAlchemy 2.0 ORM, and Pydantic schemas.
- **GNU Octave Runner (`execution_worker/runners/octave_runner.py`)**: Headless execution engine capturing standard output, error streams, vector SVG/PNG figures, and runtime workspace variables via `whos()`.
- **Python Scientific Runner (`execution_worker/runners/python_runner.py`)**: Execution sandbox with NumPy, SciPy, Matplotlib (headless `Agg` backend), and Plotly trace extraction.
- **Multi-Agent AI Orchestrator (`backend/app/ai/`)**: Contextual engineering agents (ECE Tutor, Coding Agent, Debugging Agent, Simulation Agent, Mathematics Agent, Report Agent) with OpenAI & Gemini adapters.
- **ECE Experiment Library (`backend/app/core/seed_data.py`)**: 26+ verified curriculum experiments across DSP, Communication Systems, and Control Engineering.
- **Lab Report Generator (`backend/app/services/report_service.py`)**: Automated PDF report compiler with theory, equations, code, and simulation graphs.

---

## 🛠️ Tech Stack

- **API Framework**: Python 3.12, FastAPI, Pydantic v2
- **Database**: PostgreSQL 16 (production) / SQLite async (development) with SQLAlchemy 2.0
- **Execution Runtimes**: GNU Octave 8+, Python NumPy, SciPy, SymPy, Matplotlib
- **Caching & Broker**: Redis 7, Celery
- **Document Generation**: ReportLab
- **Testing**: pytest, pytest-asyncio, HTTPX

---

## 📦 Getting Started

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)
- GNU Octave (optional, for native `.m` execution)

### 2. Setup Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate

pip install -r backend/requirements.txt email-validator greenlet
```

### 3. Initialize & Seed Database
```bash
# Windows
$env:PYTHONPATH="backend;."
python -m app.core.init_db

# Linux/macOS
export PYTHONPATH="backend:."
python -m app.core.init_db
```
*Default Credentials Created:*
- **Admin**: `admin@ece.edu` / `AdminPass123!`
- **Student**: `student@ece.edu` / `StudentPass123!`

### 4. Run Development Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation available at: `http://localhost:8000/docs`

---

## 🧪 Running Automated Tests

Run the full integration test suite and the mandatory 16-step student acceptance test:
```bash
python -m pytest tests/test_api_and_execution.py -v
python -m pytest tests/test_mandatory_e2e_student_workflow.py -v -s
```

---

## 🐳 Docker Deployment

To launch all backend services (PostgreSQL, Redis, API Gateway, and Worker):
```bash
docker compose up --build
```
