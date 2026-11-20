# ECE AI Studio - Backend & Execution Engine

Production-grade FastAPI backend and scientific execution sandbox for **ECE AI Studio**, an engineering simulation platform for Electronics and Communication Engineering students.

## 🚀 Key Modules

- **FastAPI Core (`backend/app/`)**: REST APIs, JWT authentication with bcrypt, SQLAlchemy 2.0 ORM, and Pydantic schemas.
- **GNU Octave Runner (`execution_worker/runners/octave_runner.py`)**: Headless execution engine supporting native GNU Octave runtime (`octave-cli`) with sanitized sandboxing, automatic PNG/SVG figure generation, user custom `saveas(gcf, 'sine_wave.png')` discovery, and resilient MATLAB scientific compatibility fallback.
- **Python Scientific Runner (`execution_worker/runners/python_runner.py`)**: Execution sandbox with NumPy, SciPy, Matplotlib (headless `Agg` backend), and Plotly trace extraction.
- **Multi-Agent AI Orchestrator (`backend/app/ai/`)**: Contextual engineering agents (ECE Tutor, Coding Agent, Debugging Agent, Simulation Agent, Mathematics Agent, Report Agent) with OpenAI & Gemini adapters.
- **ECE Experiment Library (`backend/app/core/seed_data.py`)**: 26+ verified curriculum experiments across DSP, Communication Systems, and Control Engineering.
- **Lab Report Generator (`backend/app/services/report_service.py`)**: Automated PDF report compiler with theory, equations, code, and simulation graphs.

---

## 🛠️ Tech Stack

- **API Framework**: Python 3.12, FastAPI, Pydantic v2
- **Database**: PostgreSQL 16 (production) / SQLite async (development) with SQLAlchemy 2.0
- **Execution Runtimes**: GNU Octave 11.3.0 / 8+, Python NumPy, SciPy, SymPy, Matplotlib
- **Caching & Broker**: Redis 7, Celery
- **Document Generation**: ReportLab
- **Testing**: pytest, pytest-asyncio, HTTPX

---

## 🎛️ GNU Octave Runtime & Execution Engine

ECE AI Studio provides a production-grade GNU Octave execution architecture designed for engineering simulations:

### 1. GNU Octave Engine Architecture
- **Executable**: GNU Octave 11.3.0 `octave-cli` (or `octave-cli.exe` on Windows).
- **Headless Execution Command**:
  ```bash
  octave-cli --no-gui --no-window-system --silent wrapper.m
  ```
- **Figure Capture**:
  - Automatically exports all active figure handles to high-resolution PNG (`-dpng -r130`) and vector SVG (`-dsvg`).
  - Discovers custom user exports such as `saveas(gcf, 'sine_wave.png')` directly from the execution sandbox.
- **Runtime Variables**:
  - Automatically captures variable name, class, dimensions, and previews via headless introspection.

### 2. Execution Security & Sandboxing
- **Directory Isolation**: Every script runs in a dedicated ephemeral directory (`temp_execution/run_oct_<uuid>`).
- **Environment Sanitization**: Strips all server secrets (`SECRET_KEY`, `DATABASE_URL`, `OPENAI_API_KEY`, etc.) before launching subprocesses.
- **Resource Limits & Timeouts**: Enforces a strict 15-second execution timeout to prevent infinite loops.
- **Cleanup**: Sandbox directories are automatically wiped via `shutil.rmtree` once generated artifacts are secured in persistent storage.
- **Resilient Fallback**: In restricted Windows environments with Code Integrity / Smart App Control policies, seamlessly evaluates MATLAB syntax via NumPy/SciPy/Matplotlib without user interruption.

---

## 📦 Getting Started

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)
- GNU Octave 8+ / 11+ (Download from [gnu.org/software/octave](https://www.gnu.org/software/octave/))

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

Run the full integration test suite, the mandatory GNU Octave sine wave test, and the end-to-end student workflow:
```bash
python -m pytest tests/test_mandatory_e2e_octave_sine_wave.py -v -s
python -m pytest tests/test_mandatory_octave_sine_wave.py -v
python -m pytest tests/test_mandatory_e2e_student_workflow.py -v -s
```

---

## 🐳 Docker Deployment

To launch all backend services (PostgreSQL, Redis, API Gateway, and Worker):
```bash
docker compose up --build
```
