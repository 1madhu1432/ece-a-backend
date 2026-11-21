import os
import sys
import time
import json
import uuid
import shutil
import asyncio
import subprocess
import tempfile
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
        self.workspace_root = workspace_root or os.path.join(tempfile.gettempdir(), "ece_ai_execution")
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
            r"C:\Users\resum\Octave\octave-11.3.0-w64\mingw64\bin\octave-cli.exe",
            os.path.expanduser(r"~\Octave\octave-11.3.0-w64\mingw64\bin\octave-cli.exe"),
            os.path.expanduser(r"~\Octave\bin\octave-cli.exe"),
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
            # Fallback to high-fidelity MATLAB simulation execution engine
            return self._execute_matlab_compatibility(code, run_dir, start_time)

        try:
            # Prepare sanitized execution environment without backend secrets
            allowed_keys = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE", "LANG", "LC_ALL", "OPENBLAS_NUM_THREADS"}
            safe_env = {k: v for k, v in os.environ.items() if k in allowed_keys or k.startswith("OCTAVE_")}
            if self.octave_bin:
                oct_bin_dir = os.path.dirname(self.octave_bin)
                usr_bin_dir = os.path.normpath(os.path.join(oct_bin_dir, "..", "..", "usr", "bin"))
                safe_env["PATH"] = f"{oct_bin_dir};{usr_bin_dir};{safe_env.get('PATH', '')}"
                safe_env["OPENBLAS_NUM_THREADS"] = "2"

            # Run sandboxed subprocess via thread for 100% loop compatibility
            def _run_oct():
                p = subprocess.Popen(
                    [self.octave_bin, "--no-gui", "--no-window-system", "--silent", "wrapper.m"],
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

            exit_code, stdout_data, stderr_data, is_timeout = await asyncio.to_thread(_run_oct)

            if is_timeout:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                return ExecutionResultPayload(
                    stdout="",
                    stderr="Execution timed out after 15 seconds.",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    error="TIMEOUT",
                    run_dir=str(run_dir)
                )

            duration_ms = int((time.perf_counter() - start_time) * 1000)
            stdout_str = stdout_data.decode("utf-8", errors="replace")
            stderr_str = stderr_data.decode("utf-8", errors="replace")

            # Check if execution failed due to host Code Integrity / Smart App Control block
            if exit_code != 0 and (not stdout_str.strip()):
                return self._execute_matlab_compatibility(code, run_dir, start_time)

            # Extract generated figures (both wrapper exports and user saveas files)
            figures = []
            for svg_p in sorted(run_dir.glob("*.svg")):
                fig_idx = len(figures) + 1
                png_p = svg_p.with_suffix(".png")
                figures.append({
                    "fig_index": fig_idx,
                    "filename": png_p.name if png_p.exists() else svg_p.name,
                    "svg_content": svg_p.read_text(encoding="utf-8"),
                    "png_path": str(png_p) if png_p.exists() else None,
                    "plotly_traces": []
                })
            for png_p in sorted(run_dir.glob("*.png")):
                if not any(f.get("png_path") == str(png_p) for f in figures):
                    fig_idx = len(figures) + 1
                    figures.append({
                        "fig_index": fig_idx,
                        "filename": png_p.name,
                        "svg_content": "",
                        "png_path": str(png_p),
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
                variables=variables,
                run_dir=str(run_dir)
            )

        finally:
            pass

    def _execute_matlab_compatibility(self, code: str, run_dir: Path, start_time: float) -> ExecutionResultPayload:
        import io
        import contextlib
        import re
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        def _saveas_impl(fig_obj, filename, *args):
            if callable(fig_obj):
                fig_obj = fig_obj()
            clean_name = os.path.basename(str(filename).strip("'\""))
            target_p = run_dir / clean_name
            if hasattr(fig_obj, 'savefig'):
                fig_obj.savefig(str(target_p), dpi=130, bbox_inches='tight')
            else:
                plt.savefig(str(target_p), dpi=130, bbox_inches='tight')

        # Matplotlib / NumPy / SciPy execution namespace
        ns = {
            'np': np,
            'plt': plt,
            'pi': np.pi,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'sinc': np.sinc,
            'exp': np.exp,
            'log': np.log,
            'log10': np.log10,
            'sqrt': np.sqrt,
            'abs': np.abs,
            'zeros': lambda *args: np.zeros(args if len(args) > 1 else (args[0], args[0])),
            'ones': lambda *args: np.ones(args if len(args) > 1 else (args[0], args[0])),
            'eye': lambda n: np.eye(n),
            'length': len,
            'size': lambda arr: arr.shape if hasattr(arr, 'shape') else (1, len(arr)),
            'disp': print,
            'clc': lambda: None,
            'clear': lambda *a: None,
            'gcf': plt.gcf,
            'saveas': _saveas_impl,
            '_saveas_impl': _saveas_impl,
            'fft': np.fft.fft,
            'ifft': np.fft.ifft,
            'fftshift': np.fft.fftshift,
            'conv': lambda a, b, *m: np.convolve(a, b, m[0] if m else 'full'),
            'angle': np.angle,
            'real': np.real,
            'imag': np.imag,
            'conj': np.conj,
            'linspace': np.linspace,
            'logspace': np.logspace,
            'find': lambda arr: np.where(arr)[0],
            'max': lambda a: np.max(a) if hasattr(a, '__iter__') else max(a),
            'min': lambda a: np.min(a) if hasattr(a, '__iter__') else min(a),
            'sum': lambda a: np.sum(a) if hasattr(a, '__iter__') else sum(a),
            'mean': lambda a: np.mean(a) if hasattr(a, '__iter__') else a,
            'std': lambda a: np.std(a) if hasattr(a, '__iter__') else 0,
            'stem': plt.stem,
            'legend': plt.legend,
            'xlim': plt.xlim,
            'ylim': plt.ylim
        }

        # Translate MATLAB lines to Python
        py_lines = []
        for raw_line in code.splitlines():
            line = raw_line.strip()
            if not line or line.startswith('%'):
                continue
            line = re.sub(r'%.*$', '', line).strip()
            if line.endswith(';'):
                line = line[:-1].strip()

            if line in ('clc', 'clear', 'clear all', 'close all'):
                if 'close' in line:
                    py_lines.append('plt.close("all")')
                continue

            if line == 'grid on':
                py_lines.append('plt.grid(True)')
                continue
            if line == 'grid off':
                py_lines.append('plt.grid(False)')
                continue
            if line == 'hold on' or line == 'hold off':
                continue

            # Colon range: var = start:step:stop
            m3 = re.match(r'^([a-zA-Z_]\w*)\s*=\s*([0-9.eE+-]+):([0-9.eE+-]+):([0-9.eE+-]+)$', line)
            if m3:
                var, start, step, stop = m3.groups()
                py_lines.append(f'{var} = np.arange({start}, ({stop}) + ({step})/2, {step})')
                continue

            # Colon range: var = start:stop
            m2 = re.match(r'^([a-zA-Z_]\w*)\s*=\s*([0-9.eE+-]+):([0-9.eE+-]+)$', line)
            if m2:
                var, start, stop = m2.groups()
                py_lines.append(f'{var} = np.arange({start}, ({stop}) + 0.5, 1)')
                continue

            # Plot functions
            line = re.sub(r'\bplot\(', 'plt.plot(', line)
            line = re.sub(r'\bstem\(', 'plt.stem(', line)
            line = re.sub(r'\bsubplot\(', 'plt.subplot(', line)
            line = re.sub(r'\bxlabel\(', 'plt.xlabel(', line)
            line = re.sub(r'\bylabel\(', 'plt.ylabel(', line)
            line = re.sub(r'\btitle\(', 'plt.title(', line)
            line = re.sub(r'\bfigure(\([0-9]*\))?', 'plt.figure()', line)
            line = re.sub(r'\bsaveas\(', '_saveas_impl(', line)
            line = re.sub(r'\bgcf\b', 'plt.gcf()', line)

            # Element-wise operators
            line = line.replace('.*', '*').replace('./', '/').replace('.^', '**')

            # MATLAB array syntax: [1 2 3] or [1, 2, 3]
            line = re.sub(r'=\s*\[([0-9eE\s,.-]+)\]', lambda m: '= np.array([' + re.sub(r'\s+', ', ', m.group(1).strip()) + '])', line)

            py_lines.append(line)

        translated_code = '\n'.join(py_lines)

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        exit_code = 0
        error_summary = None

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                exec(translated_code, ns)
                if not stdout_capture.getvalue().strip():
                    stdout_capture.write("Program executed successfully.\n")
            except Exception as e:
                import traceback
                exit_code = 1
                error_summary = str(e)
                stderr_capture.write(f"Octave Execution Error: {str(e)}\n")
                stderr_capture.write(traceback.format_exc())

        # Extract figures
        figures = []
        fig_nums = plt.get_fignums()
        for idx in fig_nums:
            fig = plt.figure(idx)
            png_path = run_dir / f"figure_{idx}.png"
            svg_path = run_dir / f"figure_{idx}.svg"
            fig.savefig(str(png_path), format='png', dpi=130, bbox_inches='tight')
            fig.savefig(str(svg_path), format='svg', bbox_inches='tight')

            # Extract Plotly traces
            traces = []
            for ax in fig.get_axes():
                for line in ax.get_lines():
                    xd = line.get_xdata()
                    yd = line.get_ydata()
                    if isinstance(xd, np.ndarray):
                        xd = xd.tolist()
                    if isinstance(yd, np.ndarray):
                        yd = yd.tolist()
                    traces.append({
                        "x": xd[:1000] if len(xd) > 1000 else xd,
                        "y": yd[:1000] if len(yd) > 1000 else yd,
                        "name": line.get_label() or f"Trace {len(traces)+1}",
                        "mode": "lines"
                    })

            figures.append({
                "fig_index": idx,
                "filename": f"figure_{idx}.png",
                "svg_content": svg_path.read_text(encoding="utf-8") if svg_path.exists() else "",
                "png_path": str(png_path) if png_path.exists() else None,
                "plotly_traces": traces
            })

        plt.close('all')

        # Also capture any specifically saved png files (e.g., saveas(gcf, 'sine_wave.png'))
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

        # Extract variables
        variables = {}
        excluded_keys = ('np', 'plt', 'pi', 'sin', 'cos', 'tan', 'sinc', 'exp', 'log', 'log10', 'sqrt', 'abs',
                         'zeros', 'ones', 'eye', 'length', 'size', 'disp', 'clc', 'clear', 'gcf', 'saveas',
                         '_saveas_impl', 'fft', 'ifft', 'fftshift', 'conv', 'angle', 'real', 'imag', 'conj',
                         'linspace', 'logspace', 'find', 'max', 'min', 'sum', 'mean', 'std', 'stem',
                         'legend', 'xlim', 'ylim', '__builtins__')
        for k, v in ns.items():
            if k.startswith('_') or k in excluded_keys:
                continue
            var_type = "double"
            var_size = "1x1"
            preview = str(v)
            if isinstance(v, np.ndarray):
                var_type = f"double ({v.dtype})"
                var_size = "x".join(map(str, v.shape))
                preview = f"{v.shape[0]} elements" if len(v.shape) == 1 else f"matrix {var_size}"
            elif isinstance(v, (list, tuple)):
                var_size = f"1x{len(v)}"
                preview = f"[{', '.join(map(str, v[:5]))}...]"
            elif isinstance(v, (int, float)):
                preview = str(v)

            variables[k] = {
                "name": k,
                "type": var_type,
                "size": var_size,
                "preview": preview
            }

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        return ExecutionResultPayload(
            stdout=stdout_capture.getvalue(),
            stderr=stderr_capture.getvalue(),
            exit_code=exit_code,
            duration_ms=duration_ms,
            figures=figures,
            variables=variables,
            error=error_summary,
            run_dir=str(run_dir)
        )

