# ECE AI Studio — AI Engineering Assistant Architecture & Verification Report

## Executive Summary

The **AI Engineering Assistant** module in ECE AI Studio delivers a domain-specialized, multi-agent artificial intelligence environment explicitly tailored for undergraduate **Electronics & Communication Engineering (B.Tech ECE)** education.

The assistant combines a provider-independent LLM layer (OpenAI, Google Gemini) with an offline domain intelligence engine (`ECEKnowledgeEngine`), providing seamless assistance, contextual code generation (MATLAB/GNU Octave `.m` and Python `.py`), runtime error root-cause diagnosis, simulation waveform analysis, and university laboratory viva examination preparation.

---

## 1. Multi-Agent Domain Architecture

### 1.1 Specialized Engineering Agents
The assistant deploys specialized agent roles with strict domain prompts:
1. **ECE Tutor**: Conceptual explanations across all 8 core disciplines with KaTeX/LaTeX mathematical formulas.
2. **Coding Agent**: Synthesizes verified, standalone `.m` and `.py` simulation scripts with vectorization and Nyquist compliance.
3. **Debugging Agent**: Parses stderr/tracebacks, identifies mathematical and runtime failure causes, and outputs 1-click correctable code.
4. **Simulation Agent**: Interprets waveform plots, calculates pole-zero stability, harmonic purity, and aliasing criteria.
5. **Mathematics Agent**: Focuses on continuous/discrete calculus, Z-transforms, Fourier analysis, and Maxwell's differential equations.
6. **Report Agent**: Formats technical observations, equipment summaries, and experimental deductions for lab reports.
7. **Viva Voce Coach**: Drills students on external examiner viva-voce questions and model answers.

### 1.2 Core Syllabus Disciplines Supported
1. **Digital Signal Processing (DSP)**: DFT, FFT, linear & circular convolution, FIR (window method) and IIR (Butterworth, Chebyshev) filter design.
2. **Analog & Digital Communication**: AM (DSB-FC, DSB-SC, SSB), FM, PM, modulation index, SNR, sampling theorem, PCM, and digital constellations.
3. **Signals and Systems**: LTI system properties, impulse response, continuous & discrete Fourier series/transforms, Laplace and Z-transforms, ROC.
4. **Control Systems**: Transfer functions, pole-zero mapping, Routh-Hurwitz stability, Root Locus, Bode plots (Gain/Phase Margins), Nyquist stability.
5. **Electronic Devices & Circuits (EDC)**: PN junction diode physics, BJT small-signal hybrid-$\pi$ models, MOSFET DC/AC analysis, op-amp circuits.
6. **Digital Electronics**: Combinational logic, Karnaugh maps, sequential logic, flip-flops (JK race-around elimination), counters, and finite state machines.
7. **Microprocessors & Microcontrollers**: 8086/8051 architectures, memory segmentation, register banks, timers, interrupts, and assembly programming.
8. **Electromagnetic Theory (EMT)**: Maxwell's equations (differential & integral forms), uniform plane wave propagation, intrinsic impedance $\eta$, skin depth, and Poynting theorem.

---

## 2. Technical Implementation Details

### 2.1 Backend Architecture
- **Adapter Pattern Providers**:
  - `BaseAIProvider`: Abstract provider interface with model override support.
  - `OpenAIProvider`: Implements GPT-4o / GPT-4o-mini integration with 15s timeout and automatic fallback.
  - `GeminiProvider`: Implements Google Gemini 1.5 Pro / Flash integration with 15s timeout.
  - `ECEKnowledgeEngine`: Offline fallback engine supplying rigorous mathematical models and code snippets when cloud API keys are unconfigured or APIs time out.
- **Context-Aware Orchestrator (`AIOrchestrator`)**:
  - Ingests active file code, Monaco editor selection, last execution error, console stdout, experiment theory, and generated plot metadata.
  - Sanitizes user input with prompt-injection guardrails against system prompt leakage and host variable access.
- **Data Model & Migrations (`AIMessage`, `AIConversation`)**:
  - Stored in SQLite/PostgreSQL with automatic dynamic schema evolution: `suggested_code TEXT` column.
  - Token quota enforcement: calculates monthly token consumption and enforces `monthly_ai_token_quota` limits (HTTP 429 when exceeded).
  - Multi-turn conversation persistence: `GET /api/v1/ai/conversations/{id}`.

### 2.2 Frontend IDE Integration
- **IDE Assistant Dock Panel (`IDEPage.tsx`)**:
  - Mode selector: Switch between AI Assistant and Lab Manual.
  - Discipline dropdown (8 ECE subjects) and Specialist Agent selector.
  - Context Sharing Toggles with visual badges: `[✓] Code`, `[✓] Selection`, `[✓] Error`, `[✓] Lab Guide`.
  - Monaco Editor selection sync: automatically captures highlighted editor lines and offers "Explain Selection".
  - Code Block Actions:
    - **Copy**: 1-click clipboard copy with checkmark visual indicator.
    - **Insert into Editor**: Inserts code into active Monaco editor tab at cursor or selection.
    - **Run in Studio**: Explicit 1-click button that inserts code and triggers execution (never executed automatically).
    - **Apply Fix to Editor**: For debugging responses, applies verified suggested code fix directly.
- **Command Window Inline Error Alert**:
  - Detects failed executions in the Command Window with an alert badge and an **"Ask AI to Debug"** button that pre-attaches error traceback and active code.
- **Simulation Artifact Inspection**:
  - Figure thumbnail cards with "Explain" button that asks the Simulation Agent to interpret the plot.

---

## 3. Verification & Automated Testing Suite

All 25 automated tests pass with 100% success rate:

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\resum\.gemini\antigravity\scratch\ece-ai-workspace\ece-a-backend
plugins: anyio-4.16.0, asyncio-1.5.0

tests/test_api_and_execution.py::test_health_check PASSED                [  4%]
tests/test_api_and_execution.py::test_auth_login_and_profile PASSED      [  8%]
tests/test_api_and_execution.py::test_project_crud_and_files PASSED      [ 12%]
tests/test_api_and_execution.py::test_python_code_execution_and_figures PASSED [ 16%]
tests/test_api_and_execution.py::test_ai_assistant_orchestration PASSED  [ 20%]
tests/test_api_and_execution.py::test_experiment_library_and_cloning PASSED [ 24%]
tests/test_api_and_execution.py::test_lab_report_generation PASSED       [ 28%]
tests/test_mandatory_e2e_octave_sine_wave.py::test_mandatory_octave_sine_wave_e2e PASSED [ 32%]
tests/test_python_dsp_execution.py::test_python_sine_wave_and_matplotlib_generation PASSED [ 36%]
tests/test_python_dsp_execution.py::test_python_fft_computation PASSED   [ 40%]
tests/test_python_dsp_execution.py::test_python_linear_convolution PASSED [ 44%]
tests/test_python_dsp_execution.py::test_python_lowpass_butterworth_filter PASSED [ 48%]
tests/test_python_dsp_execution.py::test_python_runtime_error_capture PASSED [ 52%]
tests/test_python_dsp_execution.py::test_python_timeout_handling PASSED  [ 56%]
tests/test_python_dsp_execution.py::test_python_security_sanitization PASSED [ 60%]
tests/test_python_dsp_execution.py::test_dsp_experiments_curriculum_and_cloning PASSED [ 64%]
tests/test_ai_assistant.py::test_ai_unauthenticated_request_rejected PASSED [ 68%]
tests/test_ai_assistant.py::test_ai_chat_across_all_8_ece_subjects PASSED [ 72%]
tests/test_ai_assistant.py::test_ai_code_generation_octave_and_python PASSED [ 76%]
tests/test_ai_assistant.py::test_ai_selected_code_explanation PASSED     [ 80%]
tests/test_ai_assistant.py::test_ai_runtime_error_debugging_and_suggested_code PASSED [ 84%]
tests/test_ai_assistant.py::test_ai_context_sharing_with_experiment_and_graph PASSED [ 88%]
tests/test_ai_assistant.py::test_ai_conversation_history_persistence PASSED [ 92%]
tests/test_ai_assistant.py::test_ai_viva_voce_coaching PASSED            [ 96%]
tests/test_ai_assistant.py::test_ai_prompt_injection_guardrail PASSED    [100%]

====================== 25 passed, 17 warnings in 33.81s =======================
```

Frontend production compilation (`npm run build`) succeeded with 0 TypeScript/Vite errors:
```
dist/index.html                   0.47 kB │ gzip:  0.30 kB
dist/assets/index-CebRI7jT.css   29.68 kB │ gzip:  5.85 kB
dist/assets/index-DDUgfrSs.js   321.98 kB │ gzip: 91.58 kB
✓ built in 8.11s
```
