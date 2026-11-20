import os
import sys
import time
import json
import uuid
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from execution_worker.runners.base_runner import BaseRunner, ExecutionResultPayload

OCTAVE_WRAPPER_SCRIPT = """
% ECE AI Studio Octave Headless Wrapper
try
    graphics_toolkit('gnuplot');
catch
end

try
    source('user_program.m');
catch ME
    fprintf(stderr, 'Octave Execution Error: %s\\n', ME.message);
    if length(ME.stack) > 0
        fprintf(stderr, 'In file %s at line %d\\n', ME.stack(1).name, ME.stack(1).line);
    end
end

% Intercept figures and export to SVG and PNG
try
    figHandles = findall(0, 'Type', 'figure');
    for i = 1:length(figHandles)
        fig = figHandles(i);
        set(fig, 'visible', 'off');
        svgName = sprintf('figure_%d.svg', i);
        pngName = sprintf('figure_%d.png', i);
        print(fig, svgName, '-dsvg');
        print(fig, pngName, '-dpng', '-r130');
    end
catch ME
    fprintf(stderr, 'Figure Export Warning: %s\\n', ME.message);
end

% Extract workspace variables
try
    vars = whos();
    fid = fopen('vars_dump.txt', 'w');
    for i = 1:length(vars)
        v = vars(i);
        fprintf(fid, '%s|%s|%s\\n', v.name, v.class, mat2str(v.size));
    end
    fclose(fid);
catch
end
"""

class OctaveRunner(BaseRunner):
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or str(Path.cwd() / "temp_execution")
        os.makedirs(self.workspace_root, exist_ok=True)
        self.octave_bin = self._find_octave()

    def _find_octave(self) -> Optional[str]:
        # Check PATH
        for cmd in ["octave-cli", "octave"]:
            found = shutil.which(cmd)
            if found:
                return found

        # Check typical Windows install paths
        candidates = [
            r"C:\Program Files\GNU Octave\Octave-11.3.0\mingw64\bin\octave-cli.exe",
            r"C:\Program Files\GNU Octave\Octave-9.2.0\mingw64\bin\octave-cli.exe",
            r"C:\Program Files\GNU Octave\Octave-8.4.0\mingw64\bin\octave-cli.exe",
            r"C:\Octave\octave-cli.exe"
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    async def execute(self, code: str, timeout_seconds: int = 15) -> ExecutionResultPayload:
        exec_id = str(uuid.uuid4())
        run_dir = Path(self.workspace_root) / f"run_oct_{exec_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        user_m_path = run_dir / "user_program.m"
        wrapper_path = run_dir / "wrapper.m"

        user_m_path.write_text(code, encoding="utf-8")
        wrapper_path.write_text(OCTAVE_WRAPPER_SCRIPT, encoding="utf-8")

        start_time = time.perf_counter()

        if not self.octave_bin:
            # If native Octave is not yet installed or in path,
            # we provide a clean, helpful message and fallback execution
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return ExecutionResultPayload(
                stdout="% GNU Octave Engine Notice\nInitializing MATLAB compatibility layer...",
                stderr="Notice: GNU Octave binary not found in local system PATH. Please ensure GNU Octave 8+ is installed or use Python scientific mode.",
                exit_code=1,
                duration_ms=duration_ms,
                error="OCTAVE_NOT_INSTALLED"
            )

        try:
            proc = await asyncio.create_subprocess_exec(
                self.octave_bin,
                "--no-gui",
                "--no-window-system",
                "--silent",
                "wrapper.m",
                cwd=str(run_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_seconds
                )
                exit_code = proc.returncode
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                return ExecutionResultPayload(
                    stdout="",
                    stderr="Execution timed out after 15 seconds.",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    error="TIMEOUT"
                )

            duration_ms = int((time.perf_counter() - start_time) * 1000)
            stdout_str = stdout_data.decode("utf-8", errors="replace")
            stderr_str = stderr_data.decode("utf-8", errors="replace")

            # Extract generated figures
            figures = []
            for svg_p in sorted(run_dir.glob("figure_*.svg")):
                fig_idx = int(svg_p.stem.split("_")[-1])
                png_p = run_dir / f"figure_{fig_idx}.png"
                figures.append({
                    "fig_index": fig_idx,
                    "svg_content": svg_p.read_text(encoding="utf-8"),
                    "png_path": str(png_p) if png_p.exists() else None,
                    "plotly_traces": []
                })

            # Extract variables
            variables = {}
            vars_dump_p = run_dir / "vars_dump.txt"
            if vars_dump_p.exists():
                lines = vars_dump_p.read_text(encoding="utf-8").strip().splitlines()
                for line in lines:
                    parts = line.split("|")
                    if len(parts) == 3:
                        name, var_class, size = parts
                        if name not in ("ME", "figHandles", "fig", "i", "svgName", "pngName", "vars", "fid", "v"):
                            variables[name] = {
                                "name": name,
                                "type": var_class,
                                "size": size.replace("[", "").replace("]", "").replace(" ", "x"),
                                "preview": f"{var_class} {size}"
                            }

            return ExecutionResultPayload(
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=exit_code,
                duration_ms=duration_ms,
                figures=figures,
                variables=variables
            )

        finally:
            pass
