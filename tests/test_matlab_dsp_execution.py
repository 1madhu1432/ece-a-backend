import pytest
import os
import uuid
import shutil
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database
from execution_worker.runners.octave_runner import OctaveRunner

@pytest.mark.asyncio
async def test_matlab_sine_wave_and_graphics_generation():
    """Verify MATLAB/Octave sine wave generation with dual PNG/SVG artifacts and variables."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"matlab_student_{uid}@ece.edu"
        password = "Password123!"

        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "MATLAB DSP Student",
            "college": "ECE Institute of Technology",
            "department": "ECE",
            "semester": 6
        })
        assert reg_resp.status_code == 201

        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create MATLAB project
        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"MATLAB Sine Test {uid}",
            "description": "MATLAB sine wave simulation",
            "default_engine": "octave"
        }, headers=headers)
        assert proj_resp.status_code == 201
        project = proj_resp.json()

        matlab_code = """
clear all; close all; clc;
f = 5;
fs = 500;
t = 0:1/fs:1;
x = sin(2 * pi * f * t);

figure(1);
plot(t, x, 'b-', 'LineWidth', 1.5);
title('ECE AI Studio - MATLAB Sine Wave');
xlabel('Time (seconds)');
ylabel('Amplitude');
grid on;

disp('MATLAB Sine Wave Generated Successfully.');
printf('Peak amplitude: %.2f\\n', max(x));
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project["id"],
            "code_override": matlab_code,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200
        res = exec_resp.json()
        assert res["status"] == "completed"
        assert res["exit_code"] == 0
        assert "MATLAB Sine Wave Generated Successfully" in res["results"]["stdout"]

        # Dual PNG and SVG artifacts
        assert len(res["artifacts"]) >= 2
        types = [a["artifact_type"] for a in res["artifacts"]]
        assert "figure_png" in types
        assert "figure_svg" in types

        # Workspace variables inspection
        vars_dict = res["results"]["variables_json"]
        assert "f" in vars_dict
        assert "fs" in vars_dict
        assert "x" in vars_dict

@pytest.mark.asyncio
async def test_matlab_matrix_operations():
    """Verify matrix operations: multiplication, determinant, inversion, eigenvalues."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"matrix_student_{uid}@ece.edu"
        password = "Password123!"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": password, "full_name": "Matrix Student",
            "college": "ECE", "department": "ECE", "semester": 4
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Matrix Ops {uid}", "default_engine": "octave"
        }, headers=headers)
        proj_id = proj_resp.json()["id"]

        matrix_code = """
clear all; clc;
A = [2, 1; 1, 3];
B = [1, 0; 0, 2];

% Matrix multiplication
C = A * B;

% Determinant and Inverse
detA = det(A);
invA = inv(A);

% Eigenvalues
eigA = eig(A);

disp('Matrix operations completed successfully.');
disp('Product C:'); disp(C);
disp('Determinant A:'); disp(detA);
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": matrix_code,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200
        data = exec_resp.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "Matrix operations completed successfully" in data["results"]["stdout"]
        vars_dict = data["results"]["variables_json"]
        assert "A" in vars_dict
        assert "C" in vars_dict
        assert "detA" in vars_dict

@pytest.mark.asyncio
async def test_matlab_fft_and_spectral_analysis():
    """Verify Fast Fourier Transform (FFT) and frequency peak analysis."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"fft_student_{uid}@ece.edu"
        password = "Password123!"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": password, "full_name": "FFT Student",
            "college": "ECE", "department": "ECE", "semester": 5
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"FFT Analysis {uid}", "default_engine": "octave"
        }, headers=headers)
        proj_id = proj_resp.json()["id"]

        fft_code = """
clear all; close all; clc;
fs = 1000;
N = 1024;
t = (0:N-1) / fs;
x = sin(2*pi*50*t) + 0.75*cos(2*pi*150*t);

X = fft(x);
magnitude = abs(X(1:N/2)) / (N/2);
frequencies = (0:N/2-1) * (fs / N);

figure(1);
plot(frequencies, magnitude, 'r-', 'LineWidth', 1.5);
title('FFT Spectrum: 50 Hz and 150 Hz Tones');
xlabel('Frequency (Hz)'); ylabel('Normalized Magnitude');
xlim([0 300]); grid on;

disp('FFT spectrum computed successfully.');
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": fft_code,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200
        data = exec_resp.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "FFT spectrum computed successfully" in data["results"]["stdout"]
        assert len(data["artifacts"]) >= 2

@pytest.mark.asyncio
async def test_matlab_convolution_linear_and_circular():
    """Verify linear and circular convolution."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"conv_student_{uid}@ece.edu"
        password = "Password123!"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": password, "full_name": "Conv Student",
            "college": "ECE", "department": "ECE", "semester": 5
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Conv Test {uid}", "default_engine": "octave"
        }, headers=headers)
        proj_id = proj_resp.json()["id"]

        conv_code = """
clear all; close all; clc;
x = [1, 2, 3, 2, 1];
h = [1, 1, 1];

% Linear convolution
y_lin = conv(x, h);

% Circular convolution via FFT
N = length(x) + length(h) - 1;
X_fft = fft(x, N);
H_fft = fft(h, N);
y_circ = ifft(X_fft .* H_fft);

figure(1);
subplot(2, 1, 1);
stem(0:length(y_lin)-1, y_lin, 'filled', 'b');
title('Linear Convolution y[n]'); grid on;

subplot(2, 1, 2);
stem(0:N-1, real(y_circ), 'filled', 'r');
title('Circular (Zero-Padded) Convolution y[n]'); grid on;

disp('Convolution verification completed successfully.');
disp('Linear result:'); disp(y_lin);
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": conv_code,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200
        data = exec_resp.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "Convolution verification completed successfully" in data["results"]["stdout"]

@pytest.mark.asyncio
async def test_matlab_fir_and_iir_filter_design():
    """Verify FIR and IIR digital filter design and frequency responses."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"filter_student_{uid}@ece.edu"
        password = "Password123!"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": password, "full_name": "Filter Student",
            "college": "ECE", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Filter Design {uid}", "default_engine": "octave"
        }, headers=headers)
        proj_id = proj_resp.json()["id"]

        filter_code = """
clear all; close all; clc;
fs = 2000;
fc = 200;

% 1. IIR Butterworth Filter
[b_iir, a_iir] = butter(4, fc / (fs/2), 'low');
[h_iir, w] = freqz(b_iir, a_iir, 512);

% 2. FIR Filter
b_fir = fir1(32, fc / (fs/2), 'low');
[h_fir, w2] = freqz(b_fir, 1, 512);

figure(1);
subplot(2, 1, 1);
plot((w/pi)*(fs/2), 20*log10(abs(h_iir)), 'b', 'LineWidth', 1.5);
grid on; title('IIR Butterworth Low-Pass Filter'); xlabel('Frequency (Hz)'); ylabel('Gain (dB)');

subplot(2, 1, 2);
plot((w2/pi)*(fs/2), 20*log10(abs(h_fir)), 'r', 'LineWidth', 1.5);
grid on; title('FIR Windowed Low-Pass Filter'); xlabel('Frequency (Hz)'); ylabel('Gain (dB)');

disp('FIR and IIR filter design completed.');
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": filter_code,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200
        data = exec_resp.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "FIR and IIR filter design completed" in data["results"]["stdout"]

@pytest.mark.asyncio
async def test_matlab_multiple_figures_and_pdf_report():
    """Verify multiple figures, subplots, and PDF lab report generation."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"report_student_{uid}@ece.edu"
        password = "Password123!"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": password, "full_name": "Report Student",
            "college": "ECE", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Multi-Fig Lab {uid}", "default_engine": "octave"
        }, headers=headers)
        proj_id = proj_resp.json()["id"]

        multi_fig_code = """
clear all; close all; clc;
t = 0:0.01:2;

figure(1);
plot(t, sin(2*pi*2*t), 'b-'); grid on;
title('Figure 1: 2 Hz Sine');

figure(2);
plot(t, cos(2*pi*5*t), 'r-'); grid on;
title('Figure 2: 5 Hz Cosine');

disp('Multiple figures generated.');
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": multi_fig_code,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200
        data = exec_resp.json()
        assert data["status"] == "completed"
        # 2 figures * 2 (PNG + SVG) = at least 4 artifacts
        assert len(data["artifacts"]) >= 4

        # Generate PDF report including MATLAB execution and graphs
        rep_resp = await client.post("/api/v1/reports/generate", json={
            "project_id": proj_id,
            "execution_id": data["id"],
            "title": "Comprehensive MATLAB Signal Processing Report",
            "student_name": "Report Student",
            "roll_number": "ECE-2026-999"
        }, headers=headers)
        assert rep_resp.status_code == 201
        report = rep_resp.json()
        assert report["pdf_storage_key"].endswith(".pdf")

        # Download and verify PDF bytes
        dl_resp = await client.get(report["download_url"], headers=headers)
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "application/pdf"
        assert len(dl_resp.content) > 1000

@pytest.mark.asyncio
async def test_matlab_runtime_error_handling_and_nonzero_exit():
    """Verify syntax errors and undefined functions return nonzero exit codes and clear error tracebacks."""
    runner = OctaveRunner()
    bad_code = """
clear all;
x = [1, 2, 3];
% Invalid syntax and undefined function
y = undefined_nonexistent_ece_function(x));
"""
    result = await runner.execute(bad_code, timeout_seconds=10)
    assert result.exit_code != 0
    assert result.error is not None
    assert len(result.stderr) > 0 or len(result.stdout) > 0
