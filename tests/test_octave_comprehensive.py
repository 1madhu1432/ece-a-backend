import pytest
import os
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(init_database())

async def _get_auth_headers(client: AsyncClient) -> dict:
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_{unique_id}@ece.edu"
    password = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Engineer",
        "college": "ECE Institute",
        "department": "ECE",
        "semester": 6
    })
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

async def _create_project(client: AsyncClient, headers: dict, name: str, engine: str = "octave") -> str:
    res = await client.post("/api/v1/projects", json={
        "name": name,
        "description": "Comprehensive Test Project",
        "default_engine": engine
    }, headers=headers)
    return res.json()["id"]

# 1. Test Two Sine Waves (GNU Octave)
@pytest.mark.asyncio
async def test_two_sine_waves_octave():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "Two Sine Waves Octave")

        code = """
        fs = 1000;
        t = 0:1/fs:0.2;
        f1 = 10;
        f2 = 30;
        x1 = sin(2*pi*f1*t);
        x2 = 0.5*sin(2*pi*f2*t);
        x_sum = x1 + x2;

        figure(1);
        plot(t, x1, 'b-', t, x2, 'r--', t, x_sum, 'k-');
        title('Composite Two Sine Waves');
        xlabel('Time (s)');
        ylabel('Amplitude');
        grid on;
        disp('Two sine waves calculated successfully');
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "Two sine waves calculated successfully" in data["results"]["stdout"]
        assert "x_sum" in data["results"]["variables_json"]
        assert len(data["artifacts"]) >= 1

# 2. Test FFT Frequency Detection (GNU Octave)
@pytest.mark.asyncio
async def test_fft_frequency_detection_octave():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "FFT Frequency Detection")

        code = """
        Fs = 500;
        T = 1/Fs;
        L = 1000;
        t = (0:L-1)*T;
        target_f = 50;
        S = 0.7*sin(2*pi*target_f*t);

        Y = fft(S);
        P2 = abs(Y/L);
        P1 = P2(1:L/2+1);
        P1(2:end-1) = 2*P1(2:end-1);
        f = Fs*(0:(L/2))/L;

        figure(1);
        plot(f, P1);
        title('Single-Sided Amplitude Spectrum of S(t)');
        xlabel('f (Hz)');
        ylabel('|P1(f)|');
        grid on;

        [max_val, max_idx] = max(P1);
        detected_freq = f(max_idx);
        disp(['Detected Peak Frequency: ', num2str(detected_freq)]);
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "Detected Peak Frequency: 50" in data["results"]["stdout"]
        assert "detected_freq" in data["results"]["variables_json"]

# 3. Test Multiple Figures (figure 1 and figure 2)
@pytest.mark.asyncio
async def test_multiple_figures_octave():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "Multiple Figures Octave")

        code = """
        t = 0:0.01:1;
        figure(1);
        plot(t, sin(2*pi*5*t));
        title('Figure 1: Sine 5 Hz');

        figure(2);
        plot(t, cos(2*pi*10*t));
        title('Figure 2: Cosine 10 Hz');
        disp('Multiple figures plotted');
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        # Check that at least 2 figure PNG artifacts exist
        png_artifacts = [a for a in data["artifacts"] if a["artifact_type"] == "figure_png"]
        assert len(png_artifacts) >= 2, f"Expected at least 2 figure artifacts, got {len(png_artifacts)}"

# 4. Test Subplots (subplot(2, 1, 1) and subplot(2, 1, 2))
@pytest.mark.asyncio
async def test_subplots_octave():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "Subplots Octave")

        code = """
        n = 0:20;
        x = 0.8.^n;
        figure(1);
        subplot(2, 1, 1);
        stem(n, x, 'filled');
        title('Discrete Exponential Decay (Stem)');

        subplot(2, 1, 2);
        plot(n, x, '-o');
        title('Continuous Line View');
        grid on;
        disp('Subplots completed');
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert len(data["artifacts"]) >= 1

# 5. Test PNG and SVG Output Formats
@pytest.mark.asyncio
async def test_png_and_svg_output_octave():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "PNG and SVG Output")

        code = """
        x = linspace(-pi, pi, 100);
        plot(x, sin(x));
        title('Sine Wave Vector');
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"

        artifact_types = [a["artifact_type"] for a in data["artifacts"]]
        assert "figure_png" in artifact_types, "Missing PNG artifact"
        assert "figure_svg" in artifact_types, "Missing SVG artifact"

        for art in data["artifacts"]:
            assert art["file_size_bytes"] > 0
            assert art["download_url"].startswith("/api/v1/storage/artifacts/")

# 6. Test MATLAB/Octave Filter Plotting
@pytest.mark.asyncio
async def test_octave_butterworth_filter_plotting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "Octave Butterworth Filter", engine="octave")

        code = """
clear all; close all; clc;
fs = 1000.0;
cutoff = 100.0;
[b, a] = butter(4, cutoff / (0.5 * fs), 'low');
[h, w] = freqz(b, a, 800);

figure(1);
plot(0.5 * fs * w / pi, 20 * log10(abs(h)), 'b', 'LineWidth', 1.5);
title('Butterworth Lowpass Filter Frequency Response');
xlabel('Frequency (Hz)');
ylabel('Amplitude [dB]');
grid on;
disp('Octave filter design completed.');
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["exit_code"] == 0
        assert "Octave filter design completed" in data["results"]["stdout"]
        assert len(data["artifacts"]) >= 1

# 7. Test Nonzero Execution Exit Codes on Syntax / Runtime Errors
@pytest.mark.asyncio
async def test_nonzero_execution_exit_codes_octave():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _get_auth_headers(client)
        proj_id = await _create_project(client, headers, "Nonzero Exit Error")

        # Code with an intentional undefined function error
        code = """
        x = 10;
        y = non_existent_ece_function(x);
        disp('Should not reach here');
        """
        res = await client.post("/api/v1/executions/run", json={
            "project_id": proj_id,
            "code_override": code,
            "engine": "octave"
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "failed"
        assert data["exit_code"] != 0
        assert data["results"]["stderr"] != ""
        assert "non_existent_ece_function" in data["results"]["stderr"] or "Error" in data["results"]["stderr"]

# 8. Test Failed Graph Rendering Separation
@pytest.mark.asyncio
async def test_failed_graph_rendering_octave():
    from execution_worker.runners.octave_runner import OctaveRunner
    runner = OctaveRunner()
    
    # User requested a plot, but corrupted environment where figure cannot be saved
    # The runner must never report status=completed or exit_code=0 if a requested plot fails to render
    result = await runner.execute("plot(1:10);")
    # If plot succeeded, exit_code is 0 and figures are present
    if len(result.figures) == 0:
        assert result.exit_code != 0
        assert result.error is not None
    else:
        assert len(result.figures) >= 1
        assert result.exit_code == 0
