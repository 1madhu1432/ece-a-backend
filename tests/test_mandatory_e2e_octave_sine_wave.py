import pytest
import os
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database

MANDATORY_E2E_CODE = """
t = 0:0.01:1;
f = 5;
x = sin(2*pi*f*t);

plot(t, x);
title('ECE AI Studio - Sine Wave');
xlabel('Time (seconds)');
ylabel('Amplitude');
grid on;

saveas(gcf, 'sine_wave.png');
disp('GNU Octave execution successful');
"""

@pytest.mark.asyncio
async def test_mandatory_octave_sine_wave_e2e():
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        # 1. Register a unique student user
        unique_id = uuid.uuid4().hex[:8]
        email = f"student_{unique_id}@ece.edu"
        password = "Password123!"

        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "ECE Engineering Student",
            "college": "National Institute of Technology",
            "department": "Electronics and Communication Engineering",
            "semester": 6
        })
        assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"
        user_data = reg_resp.json()

        # 2. Login to get JWT access token
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        tokens = login_resp.json()
        token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create an Octave Engineering Project
        proj_resp = await client.post("/api/v1/projects", json={
            "name": f"DSP Lab Experiment {unique_id}",
            "description": "Validation of GNU Octave Sine Wave Generation with saveas and disp",
            "default_engine": "octave"
        }, headers=headers)
        assert proj_resp.status_code == 201, f"Project creation failed: {proj_resp.text}"
        project = proj_resp.json()
        project_id = project["id"]

        # 4. Create sine_wave.m file in project
        file_resp = await client.post(f"/api/v1/projects/{project_id}/files", json={
            "name": "sine_wave.m",
            "path": "/sine_wave.m",
            "content": MANDATORY_E2E_CODE,
            "is_entrypoint": True
        }, headers=headers)
        assert file_resp.status_code == 201, f"File creation failed: {file_resp.text}"
        file_data = file_resp.json()
        file_id = file_data["id"]

        # 5. Execute using Octave engine
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project_id,
            "file_id": file_id,
            "code_override": MANDATORY_E2E_CODE,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200, f"Execution request failed: {exec_resp.text}"
        execution = exec_resp.json()

        # Verify Execution Response
        assert execution["status"] == "completed"
        assert execution["exit_code"] == 0
        assert execution["engine"] == "octave"
        assert execution["duration_ms"] > 0

        # Verify Stdout contains disp message
        stdout = execution["results"]["stdout"]
        assert "GNU Octave execution successful" in stdout, f"Expected stdout missing. Got: {stdout}"
        print("\n=== VERIFIED STDOUT ===")
        print(stdout)

        # Verify Workspace Variables
        vars_dict = execution["results"]["variables_json"]
        assert "t" in vars_dict, "Variable 't' not found in workspace"
        assert "f" in vars_dict, "Variable 'f' not found in workspace"
        assert "x" in vars_dict, "Variable 'x' not found in workspace"
        assert vars_dict["f"]["preview"] == "5"
        print("\n=== VERIFIED WORKSPACE VARIABLES ===")
        for k, v in vars_dict.items():
            print(f"  {k} ({v['type']}): size={v['size']}, preview={v['preview']}")

        # Verify Generated Figures & Artifacts (specifically sine_wave.png)
        artifacts = execution["artifacts"]
        assert len(artifacts) >= 1, "No artifacts generated"

        sine_wave_art = next((a for a in artifacts if a["filename"] == "sine_wave.png"), None)
        assert sine_wave_art is not None, f"sine_wave.png artifact not found! Available: {[a['filename'] for a in artifacts]}"
        assert sine_wave_art["artifact_type"] == "figure_png"
        assert sine_wave_art["file_size_bytes"] > 0
        assert sine_wave_art["download_url"] is not None

        print(f"\n=== VERIFIED ARTIFACT: {sine_wave_art['filename']} ===")
        print(f"  File size: {sine_wave_art['file_size_bytes']} bytes")
        print(f"  Download URL: {sine_wave_art['download_url']}")

        # 6. Fetch the artifact via the download URL and verify binary content
        art_resp = await client.get(sine_wave_art["download_url"], headers=headers)
        assert art_resp.status_code == 200, f"Failed to download artifact: {art_resp.status_code}"
        assert art_resp.headers["content-type"] == "image/png"
        img_bytes = art_resp.content
        assert len(img_bytes) == sine_wave_art["file_size_bytes"]
        # Verify PNG magic bytes: \x89PNG\r\n\x1a\n
        assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Invalid PNG header"

        # Also save a copy to the artifacts directory for evidence
        evidence_dir = r"C:\Users\resum\.gemini\antigravity\brain\1758a9c1-981d-4daa-9b79-3762129d43eb"
        if os.path.exists(evidence_dir):
            evidence_path = os.path.join(evidence_dir, "sine_wave.png")
            with open(evidence_path, "wb") as f:
                f.write(img_bytes)
            print(f"[EVIDENCE] Saved verified sine wave plot to: {evidence_path}")

        print("\n[SUCCESS] Mandatory Octave End-to-End Test PASSED with 100% verification.")
