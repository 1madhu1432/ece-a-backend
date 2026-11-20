import urllib.request
import json
import time

def test_live():
    print("==================================================")
    print("ECE AI STUDIO: LIVE FULL-STACK INTEGRATION TEST")
    print("==================================================")

    # 1. Health check
    req = urllib.request.urlopen("http://127.0.0.1:8000/healthz")
    data = json.loads(req.read().decode())
    print("[PASS] 1. Backend Health Check:", data)

    # 2. Frontend HTTP load
    req2 = urllib.request.urlopen("http://127.0.0.1:5173/")
    html = req2.read().decode()
    assert "<title>" in html
    print("[PASS] 2. Frontend HTML Served successfully (Vite on port 5173)")

    # 3. Vite reverse proxy to backend
    req3 = urllib.request.urlopen("http://127.0.0.1:5173/api/v1/experiments/categories")
    cats = json.loads(req3.read().decode())
    assert len(cats) >= 3
    print(f"[PASS] 3. Vite Reverse Proxy -> Backend: {len(cats)} curriculum categories verified")

    # 4. Student Login
    login_body = json.dumps({"email": "student@ece.edu", "password": "StudentPass123!"}).encode()
    req4 = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/login", data=login_body, headers={"Content-Type": "application/json"})
    auth_res = json.loads(urllib.request.urlopen(req4).read().decode())
    token = auth_res["access_token"]
    auth_hdr = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("[PASS] 4. Student Authentication & JWT Session Acquisition Verified")

    # 5. Create Octave Project
    proj_body = json.dumps({"name": "Live MATLAB Sine Studio Lab", "default_engine": "octave"}).encode()
    req5 = urllib.request.Request("http://127.0.0.1:8000/api/v1/projects", data=proj_body, headers=auth_hdr)
    proj = json.loads(urllib.request.urlopen(req5).read().decode())
    proj_id = proj["id"]
    print(f"[PASS] 5. Project Created: '{proj['name']}' (ID: {proj_id})")

    # 6. Execute Mandatory MATLAB Sine Program
    matlab_code = """
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
    exec_body = json.dumps({"project_id": proj_id, "code_override": matlab_code, "engine": "octave"}).encode()
    req6 = urllib.request.Request("http://127.0.0.1:8000/api/v1/executions/run", data=exec_body, headers=auth_hdr)
    exec_res = json.loads(urllib.request.urlopen(req6).read().decode())
    assert exec_res["status"] == "completed"
    assert exec_res["exit_code"] == 0
    print(f"[PASS] 6. Mandatory Octave Program Executed: status='{exec_res['status']}', exit_code={exec_res['exit_code']}, duration={exec_res['duration_ms']}ms")
    print(f"       Variables Captured: {list(exec_res['results']['variables_json'].keys())}")
    print(f"       Artifacts Generated: {len(exec_res['artifacts'])}")

    # 7. Download Artifact Figure
    assert len(exec_res["artifacts"]) >= 1
    fig = exec_res["artifacts"][0]
    art_url = "http://127.0.0.1:8000" + fig["download_url"]
    req7 = urllib.request.urlopen(art_url)
    img_data = req7.read()
    assert len(img_data) > 0
    assert req7.headers.get("Content-Type") == "image/png"
    print(f"[PASS] 7. Figure PNG Successfully Served & Verified ({len(img_data)} bytes, Content-Type: {req7.headers.get('Content-Type')})")

    # 8. AI Assistant Chat
    ai_body = json.dumps({
        "prompt": "Explain the sine wave frequency and sampling time in this code.",
        "agent_role": "ECE Tutor",
        "project_id": proj_id,
        "active_code": matlab_code
    }).encode()
    req8 = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/chat", data=ai_body, headers=auth_hdr)
    ai_res = json.loads(urllib.request.urlopen(req8).read().decode())
    assert ai_res["agent_role"] == "ECE Tutor"
    assert len(ai_res["content"]) > 20
    print(f"[PASS] 8. AI Contextual Assistant (ECE Tutor) Responded: '{ai_res['content'][:80]}...'")

    # 9. Generate PDF Lab Report
    rep_body = json.dumps({
        "project_id": proj_id,
        "title": "Sine Wave Synthesis Laboratory Report",
        "student_name": "Aarav Sharma",
        "roll_number": "ECE-2024-001"
    }).encode()
    req9 = urllib.request.Request("http://127.0.0.1:8000/api/v1/reports/generate", data=rep_body, headers=auth_hdr)
    rep_res = json.loads(urllib.request.urlopen(req9).read().decode())
    assert rep_res["id"] is not None
    print(f"[PASS] 9. Automated Lab Report Compiled: '{rep_res['title']}'")

    # 10. Download PDF Report
    rep_dl_url = "http://127.0.0.1:8000" + rep_res["download_url"]
    req10 = urllib.request.Request(rep_dl_url, headers=auth_hdr)
    pdf_data = urllib.request.urlopen(req10).read()
    assert len(pdf_data) > 1000
    assert pdf_data.startswith(b"%PDF")
    print(f"[PASS] 10. PDF Report Download Verified: {len(pdf_data)} bytes valid PDF stream")

    print("\n==================================================")
    print("ALL 10 LIVE FULL-STACK CHECKS PASSED WITH FLYING COLORS!")
    print("==================================================")

if __name__ == "__main__":
    test_live()
