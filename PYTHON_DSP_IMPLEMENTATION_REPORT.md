# ECE AI Studio – Python Scientific Computing and DSP Module Report

**Application:** ECE AI Studio  
**Modules:** Python Scientific Computing Engine, DSP Experiment Curriculum Library, MATLAB/Octave vs. Python Cross-Verification  
**Date:** November 21, 2026  
**Status:** **100% Operational & Verified**  

---

## 1. Executive Summary

The Python Scientific Computing and DSP (Digital Signal Processing) Engine has been implemented and verified across both `ece-ai-frontend` and `ece-a-backend` repositories. This provides undergraduate engineering students with a dual-paradigm simulation environment:

1. **Python Scientific Computing Stack**: Real execution powered by **Python 3.12**, **NumPy**, **SciPy**, **SymPy**, **Matplotlib**, and **Pandas**, generating PNG figures, structured variable inspection tables, and capturing output/errors.
2. **20 DSP Laboratory Experiments**: A complete, syllabus-compliant undergraduate curriculum implemented with theoretical principles, LaTeX governing equations, step-by-step procedures, expected waveforms, verified Python & Octave scripts, and interactive Viva Voce examination questions.
3. **MATLAB (.m) and Python (.py) Cross-Comparison**: One-click experiment cloning creates both `main.py` and `main_octave.m` inside the student workspace, enabling side-by-side execution, execution time profiling, and waveform verification.
4. **Interactive Lab Manual & PDF Report Generator**: An in-IDE slide-out lab guide with formula cards, procedure checklist, and click-to-reveal viva answers, alongside automated PDF lab report generation embedding execution outputs and generated plots.
5. **Zero Simulation**: Every calculation is executed by real runtimes with full security isolation.

---

## 2. Python Scientific Computing Engine Architecture

### A. Execution Pipeline

```mermaid
flowchart LR
    A["Monaco Editor (.py)"] -->|"POST /executions/run"| B["FastAPI Backend"]
    B -->|"Sandboxed Subprocess"| C["PythonRunner"]
    C -->|"Import & Execute"| D["NumPy / SciPy / SymPy / Pandas"]
    D -->|"Headless Render"| E["Matplotlib (Agg Backend)"]
    E -->|"Artifact Discovery"| F["PNG Waveforms + Variables JSON"]
    F -->|"Storage & DB"| G["Frontend Plot Viewer & Variable Table"]
```

### B. Security and Sandboxing Safeguards

- **Environment Sanitization (`safe_env`)**: The runner strips all sensitive backend secrets (`SECRET_KEY`, `DATABASE_URL`, `OPENAI_API_KEY`, etc.), allowing only standard OS runtime variables (`PATH`, `SYSTEMROOT`, `TEMP`, `PYTHONPATH`).
- **Resource Constraints**: Math library threading is clamped (`OPENBLAS_NUM_THREADS=2`, `MKL_NUM_THREADS=2`, `OMP_NUM_THREADS=2`) to prevent CPU core starvation.
- **Strict Execution Timeouts**: Enforces hard execution timeouts (30 seconds default; configurable down to 2s in tests) using `asyncio.wait_for`. Terminated processes are killed via `proc.kill()` and output buffers drained.
- **Ephemeral Sandbox Cleanup**: Executions take place in isolated `run_py_<uuid>` directories. Generated plots are copied to `/storage/artifacts/` and sandbox directories are deleted via `shutil.rmtree()`.

---

## 3. Curriculum: 20 DSP Laboratory Experiments

All 20 undergraduate DSP experiments are seeded in the database with complete metadata:

| # | Experiment Title | Slug | Key Algorithms / Libraries | Deliverables |
|---|------------------|------|----------------------------|--------------|
| 1 | Signal Generation & Basic Waveforms | `signal-generation` | NumPy, Sinusoidal / Square / Sawtooth | Continuous & Discrete plots, Viva |
| 2 | Continuous-Time & Discrete-Time Signals | `continuous-discrete-signals` | `np.linspace`, Stem plots | Time discretization comparison |
| 3 | Unit Impulse & Unit Step Sequences | `unit-impulse-step` | Dirac delta, Heaviside step | LTI singularity testing |
| 4 | Sinusoidal & Cosinusoidal Signal Analysis | `sine-cosine-signals` | Phase shifts, Quadrature | Vector phase inspection |
| 5 | Sampling Theorem & Nyquist Criteria | `sampling-theorem` | Undersampling, Critical, Sinc reconstruction | Aliasing demonstration |
| 6 | Aliasing & Foldover Frequencies | `aliasing-effect` | Frequency folding $f_{\text{alias}} = \|f_0 - k f_s\|$ | Spectrum visualization |
| 7 | Linear Convolution of Discrete Sequences | `linear-convolution` | `np.convolve`, $L_y = L_x + L_h - 1$ | Stem plot of impulse response |
| 8 | Circular Convolution & Modulo-N Indexing | `circular-convolution` | FFT circular convolution property | Linear vs. Circular comparison |
| 9 | Cross-Correlation & Signal Alignment | `cross-correlation` | `scipy.signal.correlate` | Time delay estimation (TDOA) |
| 10 | Autocorrelation & Periodicity Detection | `autocorrelation` | Energy spectral density (Wiener-Khinchin) | Pitch / Period detection |
| 11 | Fourier Series Synthesis | `fourier-series` | Harmonic summation, Gibbs phenomenon | Square wave synthesis |
| 12 | Discrete-Time Fourier Transform (DTFT) | `fourier-transform` | DTFT spectrum evaluation | Continuous frequency spectrum |
| 13 | Fast Fourier Transform (FFT & IFFT) | `fft-ifft` | `np.fft.fft`, Radix-2 Cooley-Tukey | Amplitude & Phase spectra |
| 14 | FIR Filter Design using Windows | `fir-filter-design` | `scipy.signal.firwin`, Hamming / Hann | Impulse response & frequency response |
| 15 | IIR Digital Filter Design (Bilinear Transform) | `iir-filter-design` | `scipy.signal.butter`, `bilinear` | Magnitude & Phase response |
| 16 | Low-Pass & High-Pass Filter Implementation | `lowpass-highpass-filters` | Butterworth lowpass & highpass cascade | Cutoff attenuation verification |
| 17 | Band-Pass & Band-Stop (Notch) Filters | `bandpass-bandstop-filters` | 50 Hz powerline interference notch | Narrowband rejection analysis |
| 18 | Amplitude Modulation & Demodulation | `amplitude-modulation` | DSB-FC, Modulation Index $\mu$, Envelope | Time waveform & spectra |
| 19 | Frequency Modulation (FM) & Carson's Rule | `frequency-modulation` | Frequency deviation $\Delta f$, Carson's BW | Frequency modulated waveforms |
| 20 | Power Spectral Density (PSD) Estimation | `power-spectral-density` | Welch's averaged periodogram | Noise floor & SNR estimation |

---

## 4. Frontend & Student Experience

### A. Experiment Library (`/experiments`)
- **Curriculum Filtering**: Discipline pills ("All", "Digital Signal Processing", "Communication Systems", "Control Engineering") and real-time search.
- **Dual-Engine Badges**: Visual indicators confirming dual GNU Octave (`.m`) and Python (`.py`) compatibility.
- **Lab Manual Modal**:
  - **Overview**: Aim, Theoretical Principles, Formatted Mathematical Formulas, and Laboratory Procedure.
  - **Code Comparison**: Side-by-side view of Python SciPy code and GNU Octave code with one-click copy.
  - **Viva Voce Prep**: External examiner viva questions with interactive "Reveal Model Answer" accordions.
  - **One-Click Launch**: Clones the experiment directly into the student IDE.

### B. Studio IDE (`/ide/:projectId`)
- **Automatic Engine & Language Synchronization**: Opening a `.py` file switches Monaco editor to Python syntax and defaults the execution engine to Python; opening `.m` switches to Octave syntax and Octave engine.
- **Lab Manual Drawer**: A top-bar "Lab Manual" toggle lets students read formulas, theory, and viva questions alongside the Monaco editor while coding.
- **One-Click Verified Lab Report PDF**: Compiles the student's name, college, experiment aim, theoretical principle, source code, execution stdout, and embedded simulation waveforms into a publication-ready PDF report.

---

## 5. Verification Test Matrix

All 8 automated tests in `tests/test_python_dsp_execution.py` plus regression tests passed:

| Test Name | Module Tested | Expected Behavior | Result |
|---|---|---|---|
| `test_python_sine_wave_and_matplotlib_generation` | Python Runner & Artifacts | Runs NumPy + Matplotlib, saves PNG, downloads figure, extracts variables | **PASSED** |
| `test_python_fft_computation` | SciPy / NumPy FFT | Calculates 50 Hz and 120 Hz peak frequencies accurately | **PASSED** |
| `test_python_linear_convolution` | Discrete Convolution | Computes $[1,2,3,4] * [1,1,1] = [1,3,6,9,7,4]$ | **PASSED** |
| `test_python_lowpass_butterworth_filter` | SciPy Signal IIR | Designs 4th order filter, plots frequency response | **PASSED** |
| `test_python_runtime_error_capture` | Error Tracebacks | Captures `ZeroDivisionError` with non-zero exit code | **PASSED** |
| `test_python_timeout_handling` | Process Isolation | Terminates infinite loops exceeding timeout threshold | **PASSED** |
| `test_python_security_sanitization` | Sandbox Security | Verifies 0 exposed server secrets in user environment | **PASSED** |
| `test_dsp_experiments_curriculum_and_cloning` | Curriculum API | Verifies 20+ experiments and dual `.py`/`.m` cloning | **PASSED** |
| `test_mandatory_octave_sine_wave_e2e` | GNU Octave Engine | Verifies Octave execution and `.png` export remain untouched | **PASSED** |
| Frontend TypeScript & Vite Build | Frontend Bundle | `npm run build` completed with 0 errors | **PASSED** |

---

## 6. Live Service Endpoints

- **Frontend Dev Server**: `http://127.0.0.1:5173` (Vite, React 18, Monaco Editor)
- **Backend API**: `http://127.0.0.1:8000` (FastAPI, Python 3.12, Uvicorn)
  - Health Endpoint: `GET /healthz` -> `{"status":"online","service":"ECE AI Studio"}`
  - Experiments API: `GET /api/v1/experiments` (24 curriculum experiments)
  - Execution API: `POST /api/v1/executions/run` (Supports `octave` and `python`)
  - Artifact Download: `GET /api/v1/executions/artifacts/{id}/download`
  - PDF Report Generation: `POST /api/v1/reports/generate`
