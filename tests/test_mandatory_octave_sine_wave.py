import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database

MANDATORY_MATLAB_CODE = """
clc;
clear;
close all;

t = 0:0.01:1;
f = 5;
x = sin(2*pi*f*t);

plot(t,x);
xlabel('Time');
ylabel('Amplitude');
title('Sine Wave');
grid on;
"""

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(init_database())

@pytest.mark.asyncio
async def test_mandatory_matlab_sine_wave_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as verified student
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        tokens = login_resp.json()
        token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create an Octave project
        proj_resp = await client.post("/api/v1/projects", json={
            "name": "Octave Mandatory Sine Verification",
            "description": "Validation of GNU Octave MATLAB-style sine wave simulation and graph generation",
            "default_engine": "octave"
        }, headers=headers)
        assert proj_resp.status_code == 201
        project = proj_resp.json()
        project_id = project["id"]

        # 3. Create .m file
        file_resp = await client.post(f"/api/v1/projects/{project_id}/files", json={
            "name": "sine_wave.m",
            "path": "/sine_wave.m",
            "content": MANDATORY_MATLAB_CODE,
            "is_entrypoint": True
        }, headers=headers)
        assert file_resp.status_code == 201
        file_obj = file_resp.json()
        file_id = file_obj["id"]

        # 4. Execute the MATLAB-style program using Octave engine
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project_id,
            "file_id": file_id,
            "code_override": MANDATORY_MATLAB_CODE,
            "engine": "octave"
        }, headers=headers)
        assert exec_resp.status_code == 200, f"Execution failed: {exec_resp.text}"
        execution = exec_resp.json()

        # 5. Assert execution results
        assert execution["status"] == "completed"
        assert execution["exit_code"] == 0
        assert execution["engine"] == "octave"

        results = execution["results"]
        assert results is not None
        assert "Program executed successfully" in results["stdout"] or "captured" in results["stdout"]
        print("\n[VERIFIED] Octave Standard Output:\n", results["stdout"])

        # 6. Verify Workspace Variables (t, f, x)
        vars_dict = results["variables_json"]
        assert "t" in vars_dict, "Variable 't' not found in workspace"
        assert "f" in vars_dict, "Variable 'f' not found in workspace"
        assert "x" in vars_dict, "Variable 'x' not found in workspace"
        assert vars_dict["f"]["preview"] == "5"
        assert "101" in vars_dict["t"]["size"] or "101" in vars_dict["t"]["preview"]
        assert "101" in vars_dict["x"]["size"] or "101" in vars_dict["x"]["preview"]
        print("[VERIFIED] Workspace Variables:", vars_dict)

        # 7. Verify Artifacts: Figure PNG generated and accessible
        artifacts = execution["artifacts"]
        assert len(artifacts) >= 1, "No figure artifacts generated from plot(t,x)"
        fig_art = artifacts[0]
        assert fig_art["artifact_type"] == "figure_png"
        assert fig_art["mime_type"] == "image/png"
        assert fig_art["file_size_bytes"] > 0
        assert fig_art["download_url"] is not None
        print(f"[VERIFIED] Figure generated: {fig_art['filename']} ({fig_art['file_size_bytes']} bytes), URL: {fig_art['download_url']}")

        # 8. Verify the artifact file actually exists and can be fetched
        art_get = await client.get(fig_art["download_url"], headers=headers)
        assert art_get.status_code == 200
        assert art_get.headers["content-type"] == "image/png"
        assert len(art_get.content) == fig_art["file_size_bytes"]
        print("[VERIFIED] Artifact download verified: Real PNG image rendered and served.")
