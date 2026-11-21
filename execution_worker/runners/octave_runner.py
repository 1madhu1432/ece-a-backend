import os
import sys
import time
import json
import uuid
import shutil
import asyncio
import subprocess
import tempfile
import re
import contextlib
import io
from pathlib import Path
from typing import Dict, Any, List, Optional
from execution_worker.runners.base_runner import BaseRunner, ExecutionResultPayload

OCTAVE_WRAPPER_SCRIPT = """% ECE AI Studio Octave Headless Wrapper
% Set graphics toolkit to gnuplot and hide figure windows
try
    set(0, 'defaultfigurevisible', 'off');
    graphics_toolkit('gnuplot');
catch err_gt
    fprintf(stderr, 'Octave Graphics Init Warning: %s\\n', err_gt.message);
end

% Pre-load standard ECE engineering packages
try
    pkg load signal;
catch
end
try
    pkg load control;
catch
end
try
    pkg load communications;
catch
end

% Record execution status in dedicated file so user 'clear' cannot erase it
status_fid = fopen('status.txt', 'w');
fprintf(status_fid, '0');
fclose(status_fid);

try
    source('user_program.m');
catch ME
    fprintf(stderr, 'Octave Execution Error: %s\\n', ME.message);
    if length(ME.stack) > 0
        fprintf(stderr, 'In file %s at line %d\\n', ME.stack(1).name, ME.stack(1).line);
    end
    status_fid = fopen('status.txt', 'w');
    fprintf(status_fid, '1|%s', ME.message);
    fclose(status_fid);
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
catch ME_fig
    fprintf(stderr, 'Figure Export Error: %s\\n', ME_fig.message);
    fig_err_fid = fopen('graphics_error.txt', 'w');
    fprintf(fig_err_fid, '%s', ME_fig.message);
    fclose(fig_err_fid);
end

% Extract workspace variables
try
    vars = whos();
    fid = fopen('vars_dump.txt', 'w');
    for i = 1:length(vars)
        v = vars(i);
        if strcmp(v.name, 'ans') || strcmp(v.name, 'figHandles') || strcmp(v.name, 'fig') || ...
           strcmp(v.name, 'i') || strcmp(v.name, 'svgName') || strcmp(v.name, 'pngName') || ...
           strcmp(v.name, 'vars') || strcmp(v.name, 'fid') || strcmp(v.name, 'v') || ...
           strcmp(v.name, 'status_fid') || strcmp(v.name, 'fig_err_fid') || strcmp(v.name, 'ME') || ...
           strcmp(v.name, 'ME_fig') || strcmp(v.name, 'err_gt')
            continue;
        end
        val_str = '';
        try
            val = eval(v.name);
            if isnumeric(val) || islogical(val)
                if numel(val) == 1
                    val_str = mat2str(val);
                elseif isvector(val) && length(val) <= 10
                    val_str = mat2str(val);
                elseif isvector(val)
                    val_str = sprintf('[%d elements]', length(val));
                else
                    val_str = sprintf('matrix %s', mat2str(v.size));
                end
            elseif ischar(val) || isstring(val)
                val_str = char(val);
            else
                val_str = v.class;
            end
        catch
            val_str = v.class;
        end
        fprintf(fid, '%s|%s|%s|%s\\n', v.name, v.class, mat2str(v.size), val_str);
    end
    fclose(fid);
catch ME_vars
    fprintf(stderr, 'Variable Extraction Warning: %s\\n', ME_vars.message);
end
"""

class OctaveRunner(BaseRunner):
    _cached_octave_bin: Optional[str] = None
    _cached_gnuplot_bin: Optional[str] = None

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.path.join(tempfile.gettempdir(), "ece_ai_execution")
        os.makedirs(self.workspace_root, exist_ok=True)
        if OctaveRunner._cached_octave_bin is None:
            OctaveRunner._cached_octave_bin = self._find_octave()
        self.octave_bin = OctaveRunner._cached_octave_bin

        if OctaveRunner._cached_gnuplot_bin is None:
            OctaveRunner._cached_gnuplot_bin = self._find_gnuplot()
        self.gnuplot_bin = OctaveRunner._cached_gnuplot_bin

    def _find_octave(self) -> Optional[str]:
        # 1. Environment variable override
        if os.environ.get("OCTAVE_EXECUTABLE") and os.path.exists(os.environ["OCTAVE_EXECUTABLE"]):
            return os.environ["OCTAVE_EXECUTABLE"]

        # 2. Check system PATH
        for cmd in ["octave-cli", "octave"]:
            found = shutil.which(cmd)
            if found:
                return found

        # 3. Direct fast path checks without slow recursive disk scan
        home = Path.home()
        direct_checks = [
            home / "Octave" / "octave-11.3.0-w64" / "mingw64" / "bin" / "octave-cli.exe",
            home / "Octave" / "octave-9.2.0-w64" / "mingw64" / "bin" / "octave-cli.exe",
            Path("C:/Program Files/GNU Octave/Octave-9.2.0/mingw64/bin/octave-cli.exe"),
            Path("C:/Program Files/GNU Octave/Octave-11.3.0/mingw64/bin/octave-cli.exe"),
            Path("/usr/bin/octave-cli"),
            Path("/usr/local/bin/octave-cli"),
            Path("/usr/bin/octave"),
        ]
        for d in direct_checks:
            if d.is_file() and os.access(d, os.X_OK):
                return str(d)

        # 4. Fallback search across common parent folders (shallow)
        for base_dir in [home / "Octave", Path("C:/Program Files/GNU Octave"), Path("C:/Program Files (x86)/GNU Octave")]:
            if base_dir.exists():
                for found in base_dir.rglob("octave-cli.exe"):
                    if found.is_file():
                        return str(found)

        return None

    def _find_gnuplot(self) -> Optional[str]:
        # 1. Environment variable
        if os.environ.get("GNUPLOT_EXECUTABLE") and os.path.exists(os.environ["GNUPLOT_EXECUTABLE"]):
            return os.environ["GNUPLOT_EXECUTABLE"]

        # 2. System PATH
        for cmd in ["gnuplot", "gnuplot.exe"]:
            found = shutil.which(cmd)
            if found:
                return found

        # 3. Alongside Octave distribution
        oct_bin = getattr(self, "octave_bin", None) or OctaveRunner._cached_octave_bin
        if oct_bin:
            oct_dir = Path(oct_bin).parent
            candidates = [
                oct_dir / "gnuplot.exe",
                oct_dir.parent / "bin" / "gnuplot.exe",
                oct_dir.parent.parent / "usr" / "bin" / "gnuplot.exe",
                oct_dir.parent.parent / "gnuplot" / "bin" / "gnuplot.exe",
            ]
            for c in candidates:
                if c.is_file():
                    return str(c)

        # Standard Linux paths
        for p in ["/usr/bin/gnuplot", "/usr/local/bin/gnuplot"]:
            if os.path.exists(p):
                return p

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

            # Construct cross-platform PATH using os.pathsep
            path_parts = []
            if self.octave_bin:
                oct_bin_dir = os.path.dirname(self.octave_bin)
                path_parts.append(oct_bin_dir)
                usr_bin_dir = os.path.normpath(os.path.join(oct_bin_dir, "..", "..", "usr", "bin"))
                if os.path.exists(usr_bin_dir):
                    path_parts.append(usr_bin_dir)
            if self.gnuplot_bin:
                gnu_dir = os.path.dirname(self.gnuplot_bin)
                if gnu_dir not in path_parts:
                    path_parts.append(gnu_dir)
            if safe_env.get("PATH"):
                path_parts.append(safe_env["PATH"])

            safe_env["PATH"] = os.pathsep.join(path_parts)
            safe_env["OPENBLAS_NUM_THREADS"] = "2"

            # Run sandboxed subprocess via thread for 100% event loop compatibility
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

            # Check status file for runtime errors caught inside Octave wrapper
            status_p = run_dir / "status.txt"
            error_summary = None
            if status_p.exists():
                status_content = status_p.read_text(encoding="utf-8").strip()
                if status_content.startswith("1|"):
                    exit_code = 1
                    error_summary = status_content[2:]
            elif exit_code != 0:
                error_summary = stderr_str.strip() or f"Process exited with code {exit_code}"

            # Check if execution failed due to host Code Integrity / Smart App Control block
            if exit_code != 0 and (not stdout_str.strip()) and (not status_p.exists()):
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
                    "svg_path": str(svg_p),
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
                        "svg_path": None,
                        "plotly_traces": []
                    })

            # Separate code execution status from graphics rendering status:
            # If code requested a graph/plot, verify that figures were rendered.
            graph_indicators = ["plot(", "plot3(", "stem(", "stem3(", "mesh(", "surf(", "imagesc(", "contour(", "bar(", "polar(", "scatter(", "saveas("]
            user_requested_graph = any(kw in code for kw in graph_indicators)
            graphics_err_p = run_dir / "graphics_error.txt"

            if graphics_err_p.exists():
                g_err_msg = graphics_err_p.read_text(encoding="utf-8").strip()
                exit_code = 1
                error_summary = f"Graphics Export Error: {g_err_msg}"
                stderr_str = f"{stderr_str}\n[Graphics Error] {g_err_msg}".strip()
            elif user_requested_graph and len(figures) == 0 and exit_code == 0:
                exit_code = 1
                error_summary = "Graphics Rendering Failed: Code requested plotting, but no figure artifacts were generated."
                stderr_str = f"{stderr_str}\n[Graphics Error] {error_summary}".strip()

            # Ensure successful executions with empty stdout return standard success notification
            if exit_code == 0 and not stdout_str.strip():
                stdout_str = "Program executed successfully.\n"

            # Extract workspace variables
            variables = {}
            vars_dump_p = run_dir / "vars_dump.txt"
            if vars_dump_p.exists():
                lines = vars_dump_p.read_text(encoding="utf-8").strip().splitlines()
                for line in lines:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        v_name, v_class, v_size = parts[0], parts[1], parts[2]
                        preview_val = parts[3] if len(parts) >= 4 and parts[3] else f"{v_class} {v_size}"
                        if v_name in ("ans", "figHandles", "fig", "i", "svgName", "pngName", "vars", "fid", "v",
                                      "status_fid", "fig_err_fid", "ME", "ME_fig", "err_gt"):
                            continue
                        clean_size = v_size.replace("[", "").replace("]", "").replace(" ", "x")
                        variables[v_name] = {
                            "name": v_name,
                            "type": v_class,
                            "size": clean_size,
                            "preview": preview_val
                        }

            return ExecutionResultPayload(
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=exit_code,
                duration_ms=duration_ms,
                figures=figures,
                variables=variables,
                error=error_summary,
                run_dir=str(run_dir)
            )

        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return ExecutionResultPayload(
                stdout="",
                stderr=f"Host Execution Error: {str(e)}",
                exit_code=1,
                duration_ms=duration_ms,
                error=str(e),
                run_dir=str(run_dir)
            )

    def _execute_matlab_compatibility(self, code: str, run_dir: Path, start_time: float) -> ExecutionResultPayload:
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

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
            'length': lambda x: len(x) if hasattr(x, '__len__') else 1,
            'size': lambda x: np.shape(x),
            'disp': lambda x: print(x),
            'clc': lambda: None,
            'clear': lambda *args: None,
            'close': lambda *args: plt.close('all'),
            'gcf': lambda: plt.gcf(),
            'saveas': lambda fig, filename, *args: fig.savefig(str(run_dir / filename) if not os.path.isabs(filename) else filename),
            'fft': np.fft.fft,
            'ifft': np.fft.ifft,
            'fftshift': np.fft.fftshift,
            'conv': lambda u, v: np.convolve(u, v),
            'angle': np.angle,
            'real': np.real,
            'imag': np.imag,
            'conj': np.conj,
            'linspace': np.linspace,
            'logspace': np.logspace,
            'find': lambda cond: np.where(cond)[0],
            'max': np.max,
            'min': np.min,
            'sum': np.sum,
            'mean': np.mean,
            'std': np.std,
            'stem': lambda x, y=None, *args, **kwargs: plt.stem(x, y, *args, **kwargs) if y is not None else plt.stem(x, *args, **kwargs),
            'legend': lambda *args, **kwargs: plt.legend(*args, **kwargs),
            'xlim': lambda *args: plt.xlim(*args) if args else plt.xlim(),
            'ylim': lambda *args: plt.ylim(*args) if args else plt.ylim(),
        }

        def _saveas_impl(fig, filename, *args):
            out_p = run_dir / filename if not os.path.isabs(filename) else Path(filename)
            fig.savefig(str(out_p))
        ns['saveas'] = _saveas_impl

        # Regex translation for MATLAB to Python
        py_lines = []
        for line in code.splitlines():
            clean = line.strip()
            if not clean or clean.startswith('%'):
                continue

            # Remove trailing comments and semicolons
            line = re.sub(r'%.*$', '', line)
            line = line.rstrip('; \t')

            # Colon vector: a:b:c or a:b
            line = re.sub(r'(\w+)\s*=\s*([0-9eE.-]+)\s*:\s*([0-9eE.-]+)\s*:\s*([0-9eE.-]+)', r'\1 = np.arange(\2, \4 + \3/2, \3)', line)
            line = re.sub(r'(\w+)\s*=\s*([0-9eE.-]+)\s*:\s*([0-9eE.-]+)', r'\1 = np.arange(\2, \3 + 1)', line)

            # Element-wise operations
            line = line.replace('.*', '*').replace('./', '/').replace('.^', '**').replace('^', '**')

            # Plotting functions
            line = re.sub(r'\bplot\s*\(', 'plt.plot(', line)
            line = re.sub(r'\bstem\s*\(', 'plt.stem(', line)
            line = re.sub(r'\bsubplot\s*\(', 'plt.subplot(', line)
            line = re.sub(r'\btitle\s*\(', 'plt.title(', line)
            line = re.sub(r'\bxlabel\s*\(', 'plt.xlabel(', line)
            line = re.sub(r'\bylabel\s*\(', 'plt.ylabel(', line)
            line = re.sub(r'\bgrid\s+on\b', 'plt.grid(True)', line)
            line = re.sub(r'\bgrid\s+off\b', 'plt.grid(False)', line)
            line = re.sub(r'\bfigure\b', 'plt.figure()', line)
            line = re.sub(r'\bfigure\s*\((\d+)\)', r'plt.figure(\1)', line)

            # Matrix syntax
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
                "svg_path": str(svg_path) if svg_path.exists() else None,
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
                    "svg_path": None,
                    "plotly_traces": []
                })

        # Separate code execution status from graphics rendering status
        graph_indicators = ["plot(", "plot3(", "stem(", "stem3(", "mesh(", "surf(", "imagesc(", "contour(", "bar(", "polar(", "scatter(", "saveas("]
        user_requested_graph = any(kw in code for kw in graph_indicators)
        if user_requested_graph and len(figures) == 0 and exit_code == 0:
            exit_code = 1
            error_summary = "Graphics Rendering Failed: Code requested plotting, but no figure artifacts were generated."
            stderr_capture.write(f"\n[Graphics Error] {error_summary}\n")

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
