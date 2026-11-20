import pytest
import os
import uuid
import shutil
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database
from execution_worker.runners.python_runner import PythonRunner

@pytest.mark.asyncio
async def test_python_sine_wave_and_matplotlib_generation():
    """Verify end-to-end Python script execution with NumPy and Matplotlib PNG artifact generation."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        # 1. Register & login
        uid = uuid.uuid4().hex[:8]
        email = f"py_student_{uid}@ece.edu"
        password = "Password123!"

        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Python DSP Student",
            "college": "ECE Institute of Technology",
            "department": "ECE",
            "semester": 6
        })
        assert reg_resp.status_code == 201

        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Python project
        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Python Sine Test {uid}",
            "description": "Python NumPy + Matplotlib sine wave simulation",
            "default_engine": "python"
        }, headers=headers)
        assert proj_resp.status_code == 201
        project = proj_resp.json()
        entry_file = project["files"][0]

        # 3. Execute Python Sine Wave
        python_code = """
import numpy as np
import matplotlib.pyplot as plt

f = 5
t = np.linspace(0, 1, 500)
x = np.sin(2 * np.pi * f * t)

plt.figure(figsize=(8, 4))
plt.plot(t, x, 'b-', label='5 Hz Sine')
plt.title('ECE AI Studio - Python Sine Wave')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()
plt.savefig('python_sine.png', dpi=100)
print('Python Sine Wave simulation finished successfully.')
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project["id"],
            "file_id": entry_file["id"],
            "code_override": python_code,
            "engine": "python"
        }, headers=headers)
        assert exec_resp.status_code == 200
        execution = exec_resp.json()

        assert execution["status"] == "completed"
        assert execution["exit_code"] == 0
        assert "Python Sine Wave simulation finished successfully." in execution["results"]["stdout"]

        # Verify artifacts
        artifacts = execution["artifacts"]
        assert len(artifacts) >= 1
        png_art = next((a for a in artifacts if a["filename"] == "python_sine.png" or a["artifact_type"] == "figure_png"), None)
        assert png_art is not None
        assert png_art["file_size_bytes"] > 1000

        # Verify artifact download
        dl_resp = await client.get(f"/api/v1/executions/artifacts/{png_art['id']}/download", headers=headers)
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"].startswith("image/png")
        assert len(dl_resp.content) > 1000

        # Verify structured variables
        vars_dict = execution["results"]["variables_json"]
        assert "f" in vars_dict
        assert "x" in vars_dict
        assert "t" in vars_dict

@pytest.mark.asyncio
async def test_python_fft_computation():
    """Verify Fast Fourier Transform (FFT) analysis in Python."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"fft_{uid}@ece.edu"
        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "Password123!", "full_name": "DSP Student",
            "college": "ECE Tech", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"FFT Project {uid}",
            "default_engine": "python"
        }, headers=headers)
        project = proj_resp.json()
        entry_file = project["files"][0]

        fft_code = """
import numpy as np

fs = 1000
t = np.arange(0, 1.0, 1.0/fs)
f1, f2 = 50, 120
x = 0.7 * np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)

N = len(x)
X_fft = np.fft.fft(x)
freqs = np.fft.fftfreq(N, 1.0/fs)

pos_mask = freqs > 0
peak_freq = freqs[pos_mask][np.argmax(np.abs(X_fft[pos_mask]))]
print(f'Dominant FFT Peak: {peak_freq:.1f} Hz')
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project["id"],
            "file_id": entry_file["id"],
            "code_override": fft_code,
            "engine": "python"
        }, headers=headers)
        assert exec_resp.status_code == 200
        res = exec_resp.json()
        assert res["status"] == "completed"
        assert "Dominant FFT Peak: 120.0 Hz" in res["results"]["stdout"]

@pytest.mark.asyncio
async def test_python_linear_convolution():
    """Verify Discrete Linear Convolution computation."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"conv_{uid}@ece.edu"
        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "Password123!", "full_name": "DSP Student",
            "college": "ECE Tech", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Convolution Project {uid}",
            "default_engine": "python"
        }, headers=headers)
        project = proj_resp.json()
        entry_file = project["files"][0]

        conv_code = """
import numpy as np

x = np.array([1, 2, 3, 4])
h = np.array([1, 1, 1])
y = np.convolve(x, h)

print('Input length:', len(x))
print('Impulse response length:', len(h))
print('Convolved output:', y.tolist())
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project["id"],
            "file_id": entry_file["id"],
            "code_override": conv_code,
            "engine": "python"
        }, headers=headers)
        assert exec_resp.status_code == 200
        res = exec_resp.json()
        assert res["status"] == "completed"
        assert "Convolved output: [1, 3, 6, 9, 7, 4]" in res["results"]["stdout"]

@pytest.mark.asyncio
async def test_python_lowpass_butterworth_filter():
    """Verify SciPy Butterworth Lowpass Filter design and filtering."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"filter_{uid}@ece.edu"
        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "Password123!", "full_name": "DSP Student",
            "college": "ECE Tech", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"IIR Filter Project {uid}",
            "default_engine": "python"
        }, headers=headers)
        project = proj_resp.json()
        entry_file = project["files"][0]

        filter_code = """
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

fs = 1000
cutoff = 50
order = 4
nyq = 0.5 * fs
normal_cutoff = cutoff / nyq

b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
w, h = signal.freqz(b, a, worN=800)

plt.figure(figsize=(8, 4))
plt.plot(0.5 * fs * w / np.pi, np.abs(h), 'b')
plt.axvline(cutoff, color='k', linestyle='--')
plt.title('Butterworth Lowpass Frequency Response')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain')
plt.grid(True)
plt.savefig('butterworth_response.png')

print(f'Filter order: {order}, Cutoff: {cutoff} Hz designed successfully.')
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project["id"],
            "file_id": entry_file["id"],
            "code_override": filter_code,
            "engine": "python"
        }, headers=headers)
        assert exec_resp.status_code == 200
        res = exec_resp.json()
        assert res["status"] == "completed"
        assert "Filter order: 4, Cutoff: 50 Hz designed successfully." in res["results"]["stdout"]
        assert len(res["artifacts"]) >= 1

@pytest.mark.asyncio
async def test_python_runtime_error_capture():
    """Verify structured error handling and traceback capture on Python runtime errors."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"err_{uid}@ece.edu"
        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "Password123!", "full_name": "DSP Student",
            "college": "ECE Tech", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"Error Test {uid}",
            "default_engine": "python"
        }, headers=headers)
        project = proj_resp.json()
        entry_file = project["files"][0]

        bad_code = """
import numpy as np

def broken_signal():
    return 100 / 0

broken_signal()
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project["id"],
            "file_id": entry_file["id"],
            "code_override": bad_code,
            "engine": "python"
        }, headers=headers)
        assert exec_resp.status_code == 200
        res = exec_resp.json()
        assert res["status"] == "failed"
        assert res["exit_code"] != 0
        assert "ZeroDivisionError: division by zero" in res["results"]["stderr"]

@pytest.mark.asyncio
async def test_python_timeout_handling():
    """Verify that PythonRunner terminates long-running or infinite loops exceeding timeout."""
    infinite_code = """
import time
while True:
    time.sleep(0.1)
"""
    runner = PythonRunner()
    result = await runner.execute(
        code=infinite_code,
        timeout_seconds=2
    )
    assert result.exit_code in (124, -1) or "timed out" in result.stderr.lower()
    assert "Execution timed out" in result.stderr
    # Clean up test sandbox
    if result.run_dir and os.path.exists(result.run_dir):
        shutil.rmtree(result.run_dir, ignore_errors=True)

@pytest.mark.asyncio
async def test_python_security_sanitization():
    """Verify that system secrets are not exposed in user execution environment."""
    inspect_env_code = """
import os
secrets = [k for k in os.environ.keys() if any(s in k.lower() for s in ['secret', 'key', 'token', 'password', 'database'])]
print('Exposed secrets count:', len(secrets))
"""
    runner = PythonRunner()
    result = await runner.execute(
        code=inspect_env_code,
        timeout_seconds=5
    )
    assert result.exit_code == 0
    assert "Exposed secrets count: 0" in result.stdout
    if result.run_dir and os.path.exists(result.run_dir):
        shutil.rmtree(result.run_dir, ignore_errors=True)

@pytest.mark.asyncio
async def test_dsp_experiments_curriculum_and_cloning():
    """Verify that all DSP experiments are available via API with theory, formulas, viva questions, and dual-engine cloning."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        # Check listing
        exps_resp = await client.get("/api/v1/experiments")
        assert exps_resp.status_code == 200
        exps = exps_resp.json()
        assert len(exps) >= 20

        # Check detail for sampling-theorem
        detail_resp = await client.get("/api/v1/experiments/sampling-theorem")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert "Nyquist" in detail["theory"] or "sampling" in detail["theory"].lower()
        assert len(detail["equations_json"]) >= 1
        assert detail["python_code"] is not None
        assert detail["matlab_code"] is not None
        assert len(detail["viva_questions_json"]) >= 2

        # Register user and test cloning
        uid = uuid.uuid4().hex[:8]
        email = f"cloner_{uid}@ece.edu"
        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "Password123!", "full_name": "Cloner Student",
            "college": "ECE Tech", "department": "ECE", "semester": 6
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Clone linear convolution
        clone_resp = await client.post("/api/v1/experiments/linear-convolution/clone", headers=headers)
        assert clone_resp.status_code == 200
        cloned_project = clone_resp.json()
        file_names = [f["name"] for f in cloned_project["files"]]
        # Must contain both Python and Octave files for side-by-side comparison
        assert any(fn.endswith(".py") for fn in file_names)
        assert any(fn.endswith(".m") for fn in file_names)
