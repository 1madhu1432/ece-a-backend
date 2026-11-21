import os
import sys
import time
import json
import uuid
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from execution_worker.runners.base_runner import BaseRunner, ExecutionResultPayload

WRAPPER_CODE = """
import sys
import json
import numpy as np

# Set headless Matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def _serialize_val(val):
    if isinstance(val, (int, float, str, bool)):
        return val
    elif isinstance(val, np.ndarray):
        if val.size < 50:
            return val.tolist()
        return f"Array shape {val.shape}, dtype {val.dtype}"
    elif hasattr(val, 'to_dict') and hasattr(val, 'shape'):
        return f"DataFrame {val.shape[0]} rows x {val.shape[1]} cols"
    elif hasattr(val, 'free_symbols'):
        return str(val)
    elif isinstance(val, (list, tuple)):
        return [str(v) for v in val[:20]]
    elif isinstance(val, dict):
        return {str(k): str(v) for k, v in list(val.items())[:10]}
    return str(type(val).__name__)

# Run user code in clean namespace
_user_ns = {'__name__': '__main__'}
try:
    with open('user_code.py', 'r', encoding='utf-8') as f:
        _code = f.read()
    exec(compile(_code, 'user_code.py', 'exec'), _user_ns)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 1. Capture Figures
_figures_meta = []
for fig_idx in plt.get_fignums():
    fig = plt.figure(fig_idx)
    png_file = f"figure_{fig_idx}.png"
    svg_file = f"figure_{fig_idx}.svg"
    fig.savefig(png_file, format='png', dpi=130, bbox_inches='tight')
    fig.savefig(svg_file, format='svg', bbox_inches='tight')

    # Extract axes data for Plotly interactivity
    traces = []
    for ax in fig.get_axes():
        for line in ax.get_lines():
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            if isinstance(x_data, np.ndarray):
                x_data = x_data.tolist()
            if isinstance(y_data, np.ndarray):
                y_data = y_data.tolist()
            traces.append({
                "x": x_data[:1000] if len(x_data) > 1000 else x_data,
                "y": y_data[:1000] if len(y_data) > 1000 else y_data,
                "name": line.get_label() or f"Trace {len(traces)+1}",
                "mode": "lines"
            })
    
    _figures_meta.append({
        "fig_index": fig_idx,
        "png_filename": png_file,
        "svg_filename": svg_file,
        "plotly_traces": traces
    })

# 2. Extract Variables
_vars_meta = {}
for k, v in _user_ns.items():
    if k.startswith('_') or k in ('sys', 'json', 'np', 'matplotlib', 'plt'):
        continue
    var_type = type(v).__name__
    var_size = "1x1"
    if isinstance(v, np.ndarray):
        var_type = f"ndarray ({v.dtype})"
        var_size = "x".join(map(str, v.shape))
    elif hasattr(v, 'shape') and hasattr(v, 'columns'):
        var_type = "DataFrame"
        var_size = f"{v.shape[0]}x{v.shape[1]}"
    elif hasattr(v, 'free_symbols'):
        var_type = "SymPy Expr"
        var_size = "1x1"
    elif isinstance(v, (list, tuple)):
        var_size = f"1x{len(v)}"
    _vars_meta[k] = {
        "name": k,
        "type": var_type,
        "size": var_size,
        "preview": str(_serialize_val(v))[:120]
    }

with open('output_meta.json', 'w', encoding='utf-8') as f:
    json.dump({'figures': _figures_meta, 'variables': _vars_meta}, f)
"""

class PythonRunner(BaseRunner):
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.path.join(tempfile.gettempdir(), "ece_ai_execution")
        os.makedirs(self.workspace_root, exist_ok=True)

    async def execute(self, code: str, timeout_seconds: int = 15) -> ExecutionResultPayload:
        exec_id = str(uuid.uuid4())
        run_dir = Path(self.workspace_root) / f"run_py_{exec_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        user_code_path = run_dir / "user_code.py"
        wrapper_path = run_dir / "wrapper.py"

        user_code_path.write_text(code, encoding="utf-8")
        wrapper_path.write_text(WRAPPER_CODE, encoding="utf-8")

        start_time = time.perf_counter()

        python_bin = sys.executable

        # Prepare sanitized execution environment without backend secrets
        allowed_keys = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE", "LANG", "LC_ALL", "PYTHONPATH"}
        safe_env = {k: v for k, v in os.environ.items() if k in allowed_keys}
        safe_env["PYTHONUNBUFFERED"] = "1"
        safe_env["MPLBACKEND"] = "Agg"
        safe_env["OPENBLAS_NUM_THREADS"] = "2"

        try:
            # Run sandboxed subprocess via thread to ensure 100% compatibility across all event loops (including Windows)
            def _run_proc():
                p = subprocess.Popen(
                    [python_bin, "wrapper.py"],
                    cwd=str(run_dir),
                    env=safe_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                try:
                    stdout_b, stderr_b = p.communicate(timeout=timeout_seconds)
                    return p.returncode, stdout_b, stderr_b, False
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
                    return -1, b"", b"Execution timed out after 15 seconds.", True

            exit_code, stdout_data, stderr_data, is_timeout = await asyncio.to_thread(_run_proc)

            if is_timeout:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                return ExecutionResultPayload(
                    stdout="",
                    stderr="Execution timed out after 15 seconds. Please check for infinite loops.",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    error="TIMEOUT",
                    run_dir=str(run_dir)
                )

            duration_ms = int((time.perf_counter() - start_time) * 1000)
            stdout_str = stdout_data.decode("utf-8", errors="replace")
            stderr_str = stderr_data.decode("utf-8", errors="replace")

            # Read generated output metadata
            meta_path = run_dir / "output_meta.json"
            figures = []
            variables = {}

            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    
                    for fig_info in meta.get("figures", []):
                        png_p = run_dir / fig_info["png_filename"]
                        svg_p = run_dir / fig_info["svg_filename"]
                        svg_content = svg_p.read_text(encoding="utf-8") if svg_p.exists() else ""
                        figures.append({
                            "fig_index": fig_info["fig_index"],
                            "filename": png_p.name,
                            "svg_content": svg_content,
                            "png_path": str(png_p) if png_p.exists() else None,
                            "plotly_traces": fig_info.get("plotly_traces", [])
                        })
                    
                    variables = meta.get("variables", {})
                except Exception as e:
                    stderr_str += f"\nError parsing simulation metadata: {str(e)}"

            # Also discover any user-saved PNG files (e.g. plt.savefig('custom.png'))
            for png_file in sorted(run_dir.glob("*.png")):
                if not any(f.get("filename") == png_file.name or f.get("png_path") == str(png_file) for f in figures):
                    fig_idx = len(figures) + 1
                    figures.append({
                        "fig_index": fig_idx,
                        "filename": png_file.name,
                        "svg_content": "",
                        "png_path": str(png_file),
                        "plotly_traces": []
                    })

            return ExecutionResultPayload(
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=exit_code,
                duration_ms=duration_ms,
                figures=figures,
                variables=variables,
                run_dir=str(run_dir)
            )

        finally:
            pass # Keep output files for artifact ingestion before cleanup
