import pytest
import os
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.init_db import init_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(init_database())

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "online"
        assert data["service"] == "ECE AI Studio"

@pytest.mark.asyncio
async def test_auth_login_and_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Student Login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "access_token" in token_data
        access_token = token_data["access_token"]

        # Test Get Profile
        me_resp = await client.get("/api/v1/users/me", headers={
            "Authorization": f"Bearer {access_token}"
        })
        assert me_resp.status_code == 200
        user_data = me_resp.json()
        assert user_data["email"] == "student@ece.edu"
        assert user_data["profile"]["full_name"] == "Aarav Sharma"

@pytest.mark.asyncio
async def test_project_crud_and_files():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Project
        proj_resp = await client.post("/api/v1/projects", json={
            "name": "DSP Filter Lab 1",
            "description": "Design of FIR Low Pass Filter",
            "default_engine": "octave"
        }, headers=headers)
        assert proj_resp.status_code == 201
        project = proj_resp.json()
        project_id = project["id"]
        assert project["name"] == "DSP Filter Lab 1"

        # 3. List Files
        files_resp = await client.get(f"/api/v1/projects/{project_id}/files", headers=headers)
        assert files_resp.status_code == 200
        files = files_resp.json()
        assert len(files) >= 1
        entry_file = files[0]
        assert entry_file["name"] == "main.m"

        # 4. Create New File
        create_file_resp = await client.post(f"/api/v1/projects/{project_id}/files", json={
            "name": "helper.m",
            "path": "/helper.m",
            "content": "function fs = get_sampling_rate()\nfs = 8000;\nendfunction"
        }, headers=headers)
        assert create_file_resp.status_code == 201
        assert create_file_resp.json()["name"] == "helper.m"

@pytest.mark.asyncio
async def test_matlab_code_execution_and_figures():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": "Execution Test Project",
            "default_engine": "octave"
        }, headers=headers)
        project_id = proj_resp.json()["id"]

        matlab_code = """
% ECE AI Studio - MATLAB Simulation
clear all; close all; clc;
fs = 500;
t = 0:1/fs:0.5;
freq = 10;
amplitude = 3.0;
wave = amplitude * sin(2 * pi * freq * t);
filter_taps = [0.1, 0.2, 0.4, 0.2, 0.1];

figure(1);
plot(t, wave, 'g-');
grid on;
title('Synthesized Waveform');
xlabel('Time (s)');
ylabel('Amplitude');

disp('MATLAB Simulation Completed Successfully.');
printf('Max amplitude: %.2f\\n', max(wave));
"""
        exec_resp = await client.post("/api/v1/executions/run", json={
            "project_id": project_id,
            "engine": "octave",
            "code_override": matlab_code
        }, headers=headers)
        assert exec_resp.status_code == 200
        exec_data = exec_resp.json()
        assert exec_data["status"] == "completed"
        assert exec_data["exit_code"] == 0
        assert "MATLAB Simulation Completed Successfully" in exec_data["results"]["stdout"]

        # Verify Variable Inspector captured variables
        variables = exec_data["results"]["variables_json"]
        assert "fs" in variables
        assert "wave" in variables
        assert "filter_taps" in variables

        # Verify Figure Artifact was captured
        assert len(exec_data["artifacts"]) >= 1
        artifact = exec_data["artifacts"][0]
        assert artifact["artifact_type"] == "figure_png"

@pytest.mark.asyncio
async def test_ai_assistant_orchestration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        chat_resp = await client.post("/api/v1/ai/chat", json={
            "prompt": "Explain Nyquist-Shannon Sampling Theorem in simple terms for an ECE student.",
            "agent_role": "ECE Tutor"
        }, headers=headers)
        assert chat_resp.status_code == 200
        msg = chat_resp.json()
        assert msg["sender"] == "assistant"
        assert msg["agent_role"] == "ECE Tutor"
        assert len(msg["content"]) > 50

@pytest.mark.asyncio
async def test_experiment_library_and_cloning():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cats_resp = await client.get("/api/v1/experiments/categories")
        assert cats_resp.status_code == 200
        categories = cats_resp.json()
        assert len(categories) >= 3

        exps_resp = await client.get("/api/v1/experiments")
        assert exps_resp.status_code == 200
        experiments = exps_resp.json()
        assert len(experiments) >= 5

        clone_resp = await client.post("/api/v1/experiments/sampling-theorem/clone", headers=headers)
        assert clone_resp.status_code == 200
        cloned_proj = clone_resp.json()
        assert "Sampling Theorem" in cloned_proj["name"]

@pytest.mark.asyncio
async def test_lab_report_generation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@ece.edu",
            "password": "StudentPass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        proj_resp = await client.post("/api/v1/projects", json={
            "name": "Report Test Lab",
            "default_engine": "octave"
        }, headers=headers)
        project_id = proj_resp.json()["id"]

        rep_resp = await client.post("/api/v1/reports/generate", json={
            "project_id": project_id,
            "title": "Continuous & Discrete Signals Lab",
            "student_name": "Aarav Sharma",
            "roll_number": "ECE-2023-042"
        }, headers=headers)
        assert rep_resp.status_code == 201
        report_data = rep_resp.json()
        assert report_data["title"] == "Continuous & Discrete Signals Lab"
        assert report_data["pdf_storage_key"].endswith(".pdf")

        download_resp = await client.get(report_data["download_url"], headers=headers)
        assert download_resp.status_code == 200
        assert download_resp.headers["content-type"] == "application/pdf"
        assert len(download_resp.content) > 1000
