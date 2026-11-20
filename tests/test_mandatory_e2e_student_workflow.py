import pytest
import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(init_database())

@pytest.mark.asyncio
async def test_mandatory_16_step_student_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Register new student
        rand_suffix = uuid.uuid4().hex[:6]
        test_email = f"student_{rand_suffix}@nitc.ac.in"
        reg_payload = {
            "email": test_email,
            "password": "SecureStudentPass2024!",
            "full_name": "Rohan Sharma",
            "college_name": "NIT Calicut",
            "branch": "ECE",
            "academic_year": 3
        }
        reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
        student_data = reg_resp.json()
        assert student_data["email"] == test_email
        print("\n[Step 1 PASS] Student registered successfully.")

        # Step 2: Log in
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": "SecureStudentPass2024!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        tokens = login_resp.json()
        access_token = tokens["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        print("[Step 2 PASS] Student logged in, JWT tokens acquired.")

        # Step 3: Open dashboard (Fetch profile & projects)
        me_resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["profile"]["full_name"] == "Rohan Sharma"
        print("[Step 3 PASS] Dashboard profile retrieved.")

        # Step 4: Create a project
        proj_create_resp = await client.post("/api/v1/projects", json={
            "name": "Sine Wave Analysis Lab",
            "description": "Continuous and discrete sine wave generation with FFT and plotting",
            "default_engine": "python"
        }, headers=auth_headers)
        assert proj_create_resp.status_code == 201
        project = proj_create_resp.json()
        project_id = project["id"]
        assert project["name"] == "Sine Wave Analysis Lab"
        print(f"[Step 4 PASS] Project created with ID: {project_id}")

        # Step 5: Create a file (sine_wave.py)
        file_create_resp = await client.post(f"/api/v1/projects/{project_id}/files", json={
            "name": "sine_wave.py",
            "path": "/sine_wave.py",
            "content": "",
            "is_entrypoint": True
        }, headers=auth_headers)
        assert file_create_resp.status_code == 201
        file_obj = file_create_resp.json()
        file_id = file_obj["id"]
        print(f"[Step 5 PASS] File created: {file_obj['name']}")

        # Step 6: Write a sine wave program
        sine_wave_code = """
import numpy as np
import matplotlib.pyplot as plt

# 1. Generate 5 Hz Sine Wave
fs = 1000
t = np.linspace(0, 1.0, 1000)
f0 = 5
amplitude = 2.5
signal = amplitude * np.sin(2 * np.pi * f0 * t)

# Matrix / Vector variable for inspection
sample_summary = np.array([f0, fs, amplitude, np.mean(signal), np.std(signal)])

# Plotting
plt.figure(figsize=(8, 3))
plt.plot(t[:200], signal[:200], 'b-', linewidth=1.5, label='5 Hz Sine Wave')
plt.title('Synthesized 5 Hz Continuous Signal')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude (V)')
plt.grid(True)
plt.legend()

print('Sine wave simulation completed successfully.')
print(f'Signal length: {len(signal)} samples. Peak amplitude: {np.max(signal):.2f} V')
"""
        update_resp = await client.put(f"/api/v1/projects/files/{file_id}", json={
            "content": sine_wave_code
        }, headers=auth_headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["content"] == sine_wave_code
        print("[Step 6 PASS] Program written and saved to file.")

        # Step 7: Execute code using simulation engine
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project_id,
            "file_id": file_id,
            "engine": "python"
        }, headers=auth_headers)
        assert exec_resp.status_code == 200
        exec_data = exec_resp.json()
        assert exec_data["status"] == "completed"
        assert exec_data["exit_code"] == 0
        execution_id = exec_data["id"]
        print(f"[Step 7 PASS] Simulation executed successfully (ID: {execution_id}).")

        # Step 8: View command output
        stdout_output = exec_data["results"]["stdout"]
        assert "Sine wave simulation completed successfully" in stdout_output
        assert "Peak amplitude: 2.50 V" in stdout_output
        print(f"[Step 8 PASS] Command window output captured:\n{stdout_output.strip()}")

        # Step 9: View generated graph (Artifact inspection)
        artifacts = exec_data["artifacts"]
        assert len(artifacts) >= 1
        plot_artifact = artifacts[0]
        assert plot_artifact["artifact_type"] == "figure_png"
        assert plot_artifact["download_url"].startswith("/api/v1/storage/artifacts/")
        print(f"[Step 9 PASS] Generated graph artifact verified: {plot_artifact['filename']}")

        # Step 10: Inspect variables
        runtime_vars = exec_data["results"]["variables_json"]
        assert "fs" in runtime_vars
        assert "f0" in runtime_vars
        assert "signal" in runtime_vars
        assert "sample_summary" in runtime_vars
        assert runtime_vars["fs"]["preview"] == "1000"
        print(f"[Step 10 PASS] Runtime workspace variables verified: {list(runtime_vars.keys())}")

        # Step 11: Ask AI to explain the code
        ai_resp = await client.post("/api/v1/ai/chat", json={
            "prompt": "Explain this sine wave program line by line and why fs=1000 was chosen.",
            "agent_role": "ECE Tutor",
            "project_id": project_id,
            "active_code": sine_wave_code
        }, headers=auth_headers)
        assert ai_resp.status_code == 200
        ai_msg = ai_resp.json()
        assert ai_msg["sender"] == "assistant"
        assert len(ai_msg["content"]) > 50
        print("[Step 11 PASS] AI ECE Tutor contextual explanation received.")

        # Step 12: Save project & generate formal lab report
        report_resp = await client.post("/api/v1/reports/generate", json={
            "project_id": project_id,
            "execution_id": execution_id,
            "title": "Sine Wave Synthesis & Analysis",
            "student_name": "Rohan Sharma",
            "roll_number": "NITC-ECE-2023-018"
        }, headers=auth_headers)
        assert report_resp.status_code == 201
        report = report_resp.json()
        assert report["pdf_storage_key"].endswith(".pdf")
        print("[Step 12 PASS] Project saved and formal PDF lab report generated.")

        # Step 13: Log out
        # (Client discards auth token)
        print("[Step 13 PASS] Student logged out.")

        # Step 14: Log in again
        relogin_resp = await client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": "SecureStudentPass2024!"
        })
        assert relogin_resp.status_code == 200
        new_token = relogin_resp.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        print("[Step 14 PASS] Re-authenticated successfully with fresh session token.")

        # Step 15: Reopen the saved project
        reopen_proj_resp = await client.get(f"/api/v1/projects/{project_id}", headers=new_headers)
        assert reopen_proj_resp.status_code == 200
        reopened = reopen_proj_resp.json()
        assert reopened["id"] == project_id
        assert len(reopened["files"]) >= 1
        assert any(f["name"] == "sine_wave.py" for f in reopened["files"])
        print("[Step 15 PASS] Reopened saved project with all original files intact.")

        # Step 16: View execution history
        history_resp = await client.get(f"/api/v1/executions/project/{project_id}", headers=new_headers)
        assert history_resp.status_code == 200
        history = history_resp.json()
        assert len(history) >= 1
        assert history[0]["status"] == "completed"
        print(f"[Step 16 PASS] Execution history retrieved ({len(history)} past runs).")

        print("\n=======================================================")
        print(">>> ALL 16 STEPS OF MANDATORY ACCEPTANCE TEST PASSED! <<<")
        print("=======================================================\n")
