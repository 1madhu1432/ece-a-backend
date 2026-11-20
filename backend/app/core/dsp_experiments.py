"""
ECE AI Studio - 20 DSP Undergraduate Laboratory Experiments
Comprehensive definitions with both Python (NumPy/SciPy/Matplotlib) and GNU Octave (.m) code,
formulas, procedures, expected outputs, and Viva Voce questions.
"""

DSP_EXPERIMENTS = [
    # 1. Signal Generation
    {
        "category_code": "DSP",
        "title": "Elementary Signal Generation",
        "slug": "signal-generation",
        "objective": "To synthesize and visualize fundamental standard deterministic signals: DC, ramp, exponential, and rectangular pulse.",
        "theory": (
            "Standard signals form the basis for analyzing linear time-invariant (LTI) systems. "
            "A continuous ramp is defined as r(t) = t * u(t), an exponential decay as x(t) = exp(-a*t), "
            "and a rectangular pulse of duration T as rect(t/T) = 1 for |t| <= T/2 and 0 otherwise."
        ),
        "equations_json": [
            "r(t) = t \\cdot u(t)",
            "x(t) = e^{-\\alpha t} u(t)",
            "\\text{rect}(t/T) = \\begin{cases} 1, & |t| \\le T/2 \\\\ 0, & \\text{otherwise} \\end{cases}"
        ],
        "procedure_json": [
            "Define continuous time vector t from -1 to 2 seconds",
            "Generate unit ramp signal by multiplying t with boolean condition (t >= 0)",
            "Generate decaying exponential signal with parameter alpha = 2",
            "Generate rectangular pulse centered at t = 0 with width T = 1s",
            "Plot all generated signals using subplots with appropriate labels and grids"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "t = np.linspace(-1, 2, 600)\n\n"
            "# 1. Unit Ramp Signal\n"
            "ramp = np.maximum(0, t)\n\n"
            "# 2. Decaying Exponential\n"
            "alpha = 2.0\n"
            "exp_decay = np.where(t >= 0, np.exp(-alpha * t), 0)\n\n"
            "# 3. Rectangular Pulse (width = 1.0 s)\n"
            "rect = np.where(np.abs(t) <= 0.5, 1.0, 0.0)\n\n"
            "fig, axs = plt.subplots(3, 1, figsize=(8, 7))\n"
            "axs[0].plot(t, ramp, 'b-', lw=2)\n"
            "axs[0].set_title('Unit Ramp Signal r(t)')\n"
            "axs[0].grid(True)\n\n"
            "axs[1].plot(t, exp_decay, 'r-', lw=2)\n"
            "axs[1].set_title(f'Decaying Exponential e^{{-{alpha}t}} u(t)')\n"
            "axs[1].grid(True)\n\n"
            "axs[2].plot(t, rect, 'g-', lw=2)\n"
            "axs[2].set_title('Rectangular Pulse (Width = 1.0 s)')\n"
            "axs[2].set_xlabel('Time (seconds)')\n"
            "axs[2].grid(True)\n"
            "plt.tight_layout()\n"
            "print('Elementary signals synthesized successfully.')\n"
        ),
        "python_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "t = np.linspace(-1, 2, 600)\n"
            "ramp = np.maximum(0, t)\n"
            "exp_decay = np.where(t >= 0, np.exp(-2.0 * t), 0)\n"
            "rect = np.where(np.abs(t) <= 0.5, 1.0, 0.0)\n\n"
            "fig, axs = plt.subplots(3, 1, figsize=(8, 7))\n"
            "axs[0].plot(t, ramp, 'b-', lw=2); axs[0].set_title('Ramp r(t)'); axs[0].grid(True)\n"
            "axs[1].plot(t, exp_decay, 'r-', lw=2); axs[1].set_title('Exponential e^{-2t}'); axs[1].grid(True)\n"
            "axs[2].plot(t, rect, 'g-', lw=2); axs[2].set_title('Rectangular Pulse'); axs[2].grid(True)\n"
            "plt.tight_layout()\n"
            "print('Elementary signals synthesized successfully.')\n"
        ),
        "matlab_code": (
            "% Elementary Signal Generation\n"
            "clear all; close all; clc;\n"
            "t = -1:0.005:2;\n"
            "ramp = max(0, t);\n"
            "exp_decay = exp(-2 * t) .* (t >= 0);\n"
            "rect = (abs(t) <= 0.5);\n\n"
            "figure(1);\n"
            "subplot(3,1,1); plot(t, ramp, 'b', 'LineWidth', 1.5); grid on; title('Unit Ramp');\n"
            "subplot(3,1,2); plot(t, exp_decay, 'r', 'LineWidth', 1.5); grid on; title('Exponential');\n"
            "subplot(3,1,3); plot(t, rect, 'g', 'LineWidth', 1.5); grid on; title('Rect Pulse');\n"
            "disp('Elementary signals synthesized successfully.');\n"
        ),
        "expected_output": "Elementary signals synthesized successfully.",
        "viva_questions_json": [
            {"question": "What is the derivative of a unit ramp signal with respect to time?", "answer": "The derivative of a unit ramp r(t) is the unit step signal u(t)."},
            {"question": "What is the mathematical area under an ideal Dirac delta function?", "answer": "The area under an ideal Dirac delta function over all real numbers is strictly equal to 1."},
            {"question": "Distinguish between continuous-time energy signals and power signals.", "answer": "An energy signal has finite total energy (0 < E < infinity) and zero average power, while a power signal has finite non-zero average power (0 < P < infinity) and infinite total energy."}
        ]
    },

    # 2. Continuous-time and Discrete-time Signals
    {
        "category_code": "DSP",
        "title": "Continuous-Time vs Discrete-Time Signals",
        "slug": "continuous-discrete-signals",
        "objective": "To demonstrate the transformation of continuous-time waveforms x(t) into discrete-time sequences x[n] via periodic sampling.",
        "theory": (
            "A continuous-time signal x(t) is defined for every continuum point t in R. "
            "A discrete-time sequence x[n] is defined solely at integer index values n. "
            "Sampling an analog signal x(t) with uniform sampling interval Ts = 1/fs yields x[n] = x(n * Ts)."
        ),
        "equations_json": [
            "x(t) = A \\cos(2\\pi f_0 t + \\phi)",
            "x[n] = x(n T_s) = A \\cos\\left(2\\pi \\frac{f_0}{f_s} n + \\phi\\right)",
            "\\omega_0 = 2\\pi \\frac{f_0}{f_s} \\text{ (normalized digital frequency)}"
        ],
        "procedure_json": [
            "Define an analog sinusoidal signal with frequency f0 = 5 Hz sampled densely at 2000 Hz",
            "Sample the signal at a discrete rate of fs = 40 Hz",
            "Plot continuous waveform x(t) as a smooth line and x[n] using discrete stem markers",
            "Overlay both representations to observe sampling correspondence"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "f0 = 5.0          # Signal frequency 5 Hz\n"
            "t_dense = np.linspace(0, 0.5, 1000)\n"
            "x_dense = np.sin(2 * np.pi * f0 * t_dense)\n\n"
            "fs = 40.0         # Sampling rate 40 Hz\n"
            "n = np.arange(0, 21)\n"
            "t_discrete = n / fs\n"
            "x_discrete = np.sin(2 * np.pi * f0 * t_discrete)\n\n"
            "plt.figure(figsize=(9, 5))\n"
            "plt.plot(t_dense, x_dense, 'b-', label='Continuous x(t) (5 Hz)', alpha=0.7)\n"
            "plt.stem(t_discrete, x_discrete, linefmt='r-', markerfmt='ro', basefmt='k-', label='Discrete Samples x[n]')\n"
            "plt.title('Continuous vs Discrete Representation of a 5 Hz Sinusoid')\n"
            "plt.xlabel('Time (seconds)')\n"
            "plt.ylabel('Amplitude')\n"
            "plt.grid(True)\n"
            "plt.legend()\n"
            "print(f'Total discrete samples taken: {len(n)}')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "f0 = 5.0; t_c = np.linspace(0, 0.5, 1000); x_c = np.sin(2*np.pi*f0*t_c)\n"
            "fs = 40.0; n = np.arange(21); t_d = n / fs; x_d = np.sin(2*np.pi*f0*t_d)\n"
            "plt.figure(figsize=(8, 4))\n"
            "plt.plot(t_c, x_c, 'b-', label='Analog x(t)'); plt.stem(t_d, x_d, 'r', label='Discrete x[n]')\n"
            "plt.title('Continuous vs Discrete Comparison'); plt.legend(); plt.grid(True)\n"
            "print(f'Discrete samples: {len(n)}')\n"
        ),
        "matlab_code": (
            "% Continuous vs Discrete Signals\n"
            "clear all; close all; clc;\n"
            "f0 = 5; tc = 0:0.0005:0.5; xc = sin(2*pi*f0*tc);\n"
            "fs = 40; n = 0:20; td = n / fs; xd = sin(2*pi*f0*td);\n"
            "figure(1);\n"
            "plot(tc, xc, 'b-', 'LineWidth', 1.5); hold on;\n"
            "stem(td, xd, 'r', 'filled', 'LineWidth', 1.2); hold off;\n"
            "grid on; title('Continuous vs Discrete Signals');\n"
            "legend('Continuous x(t)', 'Discrete x[n]');\n"
            "disp(['Discrete samples: ', num2str(length(n))]);\n"
        ),
        "expected_output": "Total discrete samples taken: 21",
        "viva_questions_json": [
            {"question": "Why is the independent variable 'n' dimensionless in discrete time?", "answer": "The variable 'n' is an integer sequence index denoting the count of sample steps, not physical seconds."},
            {"question": "What is the maximum unique frequency in a discrete-time sinusoid?", "answer": "The normalized digital frequency omega is unique only over a 2*pi interval, typically [-pi, +pi], corresponding to half the sampling rate (fs/2)."}
        ]
    },

    # 3. Unit Impulse and Unit Step Signals
    {
        "category_code": "DSP",
        "title": "Unit Impulse and Unit Step Sequences",
        "slug": "unit-impulse-step",
        "objective": "To generate standard elementary discrete-time signals: unit impulse delta[n] and unit step u[n] with time shifts.",
        "theory": (
            "The discrete unit impulse is defined as delta[n] = 1 for n = 0 and 0 otherwise. "
            "The discrete unit step is defined as u[n] = 1 for n >= 0 and 0 for n < 0. "
            "A delayed impulse delta[n-k] exhibits its non-zero value at index n = k."
        ),
        "equations_json": [
            "\\delta[n] = \\begin{cases} 1, & n = 0 \\\\ 0, & n \\neq 0 \\end{cases}",
            "u[n] = \\sum_{k=0}^{\\infty} \\delta[n-k] = \\begin{cases} 1, & n \\ge 0 \\\\ 0, & n < 0 \\end{cases}",
            "\\delta[n] = u[n] - u[n-1]"
        ],
        "procedure_json": [
            "Define sample index vector n from -10 to 10",
            "Synthesize delta[n] using equality condition (n == 0)",
            "Synthesize delayed step sequence u[n-3] using inequality (n >= 3)",
            "Display both sequences using discrete stem graphs"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "n = np.arange(-10, 11)\n"
            "delta = (n == 0).astype(float)\n"
            "delta_delayed = (n == 3).astype(float)\n"
            "u = (n >= 0).astype(float)\n"
            "u_delayed = (n >= 2).astype(float)\n\n"
            "fig, axs = plt.subplots(2, 2, figsize=(10, 6))\n"
            "axs[0, 0].stem(n, delta, linefmt='b-', markerfmt='bo')\n"
            "axs[0, 0].set_title('Unit Impulse \\delta[n]'); axs[0, 0].grid(True)\n\n"
            "axs[0, 1].stem(n, delta_delayed, linefmt='m-', markerfmt='mo')\n"
            "axs[0, 1].set_title('Delayed Impulse \\delta[n - 3]'); axs[0, 1].grid(True)\n\n"
            "axs[1, 0].stem(n, u, linefmt='g-', markerfmt='go')\n"
            "axs[1, 0].set_title('Unit Step u[n]'); axs[1, 0].grid(True)\n\n"
            "axs[1, 1].stem(n, u_delayed, linefmt='r-', markerfmt='ro')\n"
            "axs[1, 1].set_title('Delayed Step u[n - 2]'); axs[1, 1].grid(True)\n\n"
            "plt.tight_layout()\n"
            "print('Impulse and step sequences generated.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "n = np.arange(-10, 11); delta = (n == 0).astype(float); u = (n >= 0).astype(float)\n"
            "fig, axs = plt.subplots(2, 1, figsize=(8, 5))\n"
            "axs[0].stem(n, delta); axs[0].set_title('delta[n]'); axs[0].grid(True)\n"
            "axs[1].stem(n, u); axs[1].set_title('u[n]'); axs[1].grid(True)\n"
            "plt.tight_layout()\n"
            "print('Impulse and step sequences generated.')\n"
        ),
        "matlab_code": (
            "% Unit Impulse & Step Sequences\n"
            "clear all; close all; clc;\n"
            "n = -10:1:10; delta = (n == 0); u = (n >= 0);\n"
            "figure(1);\n"
            "subplot(2,1,1); stem(n, delta, 'b', 'filled'); grid on; title('\\delta[n]');\n"
            "subplot(2,1,2); stem(n, u, 'm', 'filled'); grid on; title('u[n]');\n"
            "disp('Impulse and step sequences generated.');\n"
        ),
        "expected_output": "Impulse and step sequences generated.",
        "viva_questions_json": [
            {"question": "How can the unit impulse be obtained from the unit step sequence?", "answer": "By backward differencing: delta[n] = u[n] - u[n-1]."},
            {"question": "What is the physical interpretation of an LTI system's impulse response h[n]?", "answer": "The impulse response h[n] is the output of the LTI system when excited by delta[n]; it completely characterizes the linear time-invariant system."}
        ]
    },

    # 4. Sine and Cosine Signals
    {
        "category_code": "DSP",
        "title": "Sine and Cosine Signals & Phase Orthogonality",
        "slug": "sine-cosine-signals",
        "objective": "To synthesize harmonically related sine and cosine waveforms and demonstrate their 90-degree phase shift and orthogonality.",
        "theory": (
            "Sinusoidal signals are fundamental eigenfunctions of LTI systems. "
            "A cosine wave is related to a sine wave by cos(2*pi*f*t) = sin(2*pi*f*t + pi/2). "
            "Over any integer number of cycles, the inner product of sine and cosine at the same frequency is identically zero."
        ),
        "equations_json": [
            "x_1(t) = A \\cos(2\\pi f_0 t)",
            "x_2(t) = A \\sin(2\\pi f_0 t) = A \\cos(2\\pi f_0 t - \\pi/2)",
            "\\int_0^{T_0} x_1(t) x_2(t) dt = 0 \\text{ (Orthogonality)}"
        ],
        "procedure_json": [
            "Create time vector t over two complete periods for f0 = 10 Hz",
            "Compute sine and cosine waveforms with amplitude A = 3",
            "Calculate point-wise product x1 * x2 and compute integral to verify orthogonality",
            "Plot sine, cosine, and their instantaneous product"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "f0 = 10.0          # 10 Hz\n"
            "T0 = 1.0 / f0\n"
            "t = np.linspace(0, 2 * T0, 500)\n\n"
            "A = 3.0\n"
            "cosine_wave = A * np.cos(2 * np.pi * f0 * t)\n"
            "sine_wave = A * np.sin(2 * np.pi * f0 * t)\n"
            "product = cosine_wave * sine_wave\n\n"
            "inner_product = np.trapz(product, t)\n\n"
            "plt.figure(figsize=(9, 6))\n"
            "plt.subplot(2, 1, 1)\n"
            "plt.plot(t, cosine_wave, 'b-', lw=1.8, label='Cosine: 3 cos(2*pi*10*t)')\n"
            "plt.plot(t, sine_wave, 'r--', lw=1.8, label='Sine: 3 sin(2*pi*10*t)')\n"
            "plt.title('Harmonic Sine and Cosine Waves (90° Phase Difference)')\n"
            "plt.grid(True); plt.legend()\n\n"
            "plt.subplot(2, 1, 2)\n"
            "plt.plot(t, product, 'g-', lw=1.5, label='Product: sin(t) * cos(t)')\n"
            "plt.axhline(0, color='k', linestyle=':')\n"
            "plt.title(f'Pointwise Product (Integral over 2 cycles = {inner_product:.4e})')\n"
            "plt.xlabel('Time (s)')\n"
            "plt.grid(True); plt.legend()\n"
            "plt.tight_layout()\n"
            "print(f'Orthogonality integral result: {inner_product:.6f}')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "f0 = 10; t = np.linspace(0, 0.2, 500)\n"
            "s = np.sin(2*np.pi*f0*t); c = np.cos(2*np.pi*f0*t)\n"
            "plt.figure(figsize=(8, 4))\n"
            "plt.plot(t, s, 'r--', label='Sine'); plt.plot(t, c, 'b-', label='Cosine')\n"
            "plt.legend(); plt.grid(True); plt.title('Sine and Cosine Signals')\n"
            "print('Sine and cosine generated.')\n"
        ),
        "matlab_code": (
            "% Sine & Cosine Signals\n"
            "clear all; close all; clc;\n"
            "f0 = 10; t = 0:0.0005:0.2;\n"
            "s = sin(2*pi*f0*t); c = cos(2*pi*f0*t);\n"
            "figure(1);\n"
            "plot(t, s, 'r--', t, c, 'b-', 'LineWidth', 1.5);\n"
            "grid on; title('Sine & Cosine Signals'); legend('Sine', 'Cosine');\n"
            "disp('Sine and cosine generated.');\n"
        ),
        "expected_output": "Orthogonality integral result: 0.000000",
        "viva_questions_json": [
            {"question": "Why are sinusoids termed eigenfunctions of linear time-invariant systems?", "answer": "When a sinusoid of frequency f0 is input to an LTI system, the output is guaranteed to be a sinusoid of the exact same frequency f0, altered only in amplitude and phase."},
            {"question": "What is the trigonometric identity for sin(A) * cos(A)?", "answer": "sin(A) * cos(A) = 0.5 * sin(2A), which oscillates at twice the fundamental frequency with zero mean."}
        ]
    },

    # 5. Sampling Theorem
    {
        "category_code": "DSP",
        "title": "Verification of Nyquist-Shannon Sampling Theorem",
        "slug": "sampling-theorem",
        "objective": "To observe and verify the Nyquist criterion for signal reconstruction without information loss.",
        "theory": (
            "The Nyquist-Shannon sampling theorem states that an analog bandlimited signal with highest "
            "frequency component f_max can be perfectly reconstructed from its discrete samples if and only if "
            "the sampling frequency satisfies fs >= 2 * f_max. The critical sampling rate 2 * f_max is the Nyquist rate."
        ),
        "equations_json": [
            "f_s \\ge 2 f_{max} \\text{ (Nyquist Criterion)}",
            "T_s \\le \\frac{1}{2 f_{max}} \\text{ (Maximum Sampling Period)}",
            "x(t) = \\sum_{n=-\\infty}^{\\infty} x[n] \\text{sinc}\\left(\\frac{t - n T_s}{T_s}\\right) \\text{ (Whittaker-Shannon Formula)}"
        ],
        "procedure_json": [
            "Generate an analog reference sinusoid at frequency fm = 15 Hz",
            "Simulate under-sampling with fs = 20 Hz (< 2*fm)",
            "Simulate critical sampling with fs = 30 Hz (= 2*fm)",
            "Simulate over-sampling with fs = 150 Hz (>> 2*fm)",
            "Plot and compare the reconstructed continuous waveforms"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "fm = 15.0         # 15 Hz analog signal\n"
            "t_analog = np.linspace(0, 0.25, 2000)\n"
            "x_analog = np.sin(2 * np.pi * fm * t_analog)\n\n"
            "# 1. Under-sampling (fs1 = 20 Hz < 30 Hz)\n"
            "fs1 = 20.0; t1 = np.arange(0, 0.25, 1/fs1); x1 = np.sin(2 * np.pi * fm * t1)\n\n"
            "# 2. Critical Nyquist sampling (fs2 = 30 Hz = 2*fm)\n"
            "fs2 = 30.0; t2 = np.arange(0, 0.25, 1/fs2); x2 = np.sin(2 * np.pi * fm * t2)\n\n"
            "# 3. Over-sampling (fs3 = 180 Hz >> 2*fm)\n"
            "fs3 = 180.0; t3 = np.arange(0, 0.25, 1/fs3); x3 = np.sin(2 * np.pi * fm * t3)\n\n"
            "fig, axs = plt.subplots(3, 1, figsize=(9, 7))\n"
            "axs[0].plot(t_analog, x_analog, 'k--', label='True 15 Hz Signal')\n"
            "axs[0].plot(t1, x1, 'ro-', label='Sampled at 20 Hz (Under-sampled)')\n"
            "axs[0].set_title('Case 1: Under-sampling (fs < 2*fm) -> Severe Aliasing')\n"
            "axs[0].grid(True); axs[0].legend(loc='upper right')\n\n"
            "axs[1].plot(t_analog, x_analog, 'k--')\n"
            "axs[1].plot(t2, x2, 'bo-', label='Sampled at 30 Hz (Nyquist Rate)')\n"
            "axs[1].set_title('Case 2: Critical Sampling (fs = 2*fm)')\n"
            "axs[1].grid(True); axs[1].legend(loc='upper right')\n\n"
            "axs[2].plot(t_analog, x_analog, 'k--')\n"
            "axs[2].plot(t3, x3, 'go-', label='Sampled at 180 Hz (Over-sampled)')\n"
            "axs[2].set_title('Case 3: Over-sampling (fs >> 2*fm) -> Faithful Recovery')\n"
            "axs[2].set_xlabel('Time (s)')\n"
            "axs[2].grid(True); axs[2].legend(loc='upper right')\n\n"
            "plt.tight_layout()\n"
            "print('Nyquist sampling theorem simulation completed.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "fm = 15.0; t_c = np.linspace(0, 0.25, 1000); x_c = np.sin(2*np.pi*fm*t_c)\n"
            "for fs, col, label in [(20, 'r', 'Under'), (30, 'b', 'Critical'), (150, 'g', 'Over')]:\n"
            "    t_s = np.arange(0, 0.25, 1/fs); x_s = np.sin(2*np.pi*fm*t_s)\n"
            "    plt.plot(t_s, x_s, f'{col}o-', label=f'{label} fs={fs}Hz')\n"
            "plt.plot(t_c, x_c, 'k--', alpha=0.5, label='True Signal')\n"
            "plt.legend(); plt.grid(True); plt.title('Sampling Comparison')\n"
            "print('Nyquist sampling theorem verified.')\n"
        ),
        "matlab_code": (
            "% Nyquist Sampling Theorem\n"
            "clear all; close all; clc;\n"
            "fm = 15; tc = 0:0.0002:0.25; xc = sin(2*pi*fm*tc);\n"
            "fs1 = 20; t1 = 0:1/fs1:0.25; x1 = sin(2*pi*fm*t1);\n"
            "fs2 = 30; t2 = 0:1/fs2:0.25; x2 = sin(2*pi*fm*t2);\n"
            "fs3 = 150; t3 = 0:1/fs3:0.25; x3 = sin(2*pi*fm*t3);\n"
            "figure(1);\n"
            "subplot(3,1,1); plot(tc, xc, 'k--', t1, x1, 'r-o'); grid on; title('Under-sampled fs=20Hz');\n"
            "subplot(3,1,2); plot(tc, xc, 'k--', t2, x2, 'b-o'); grid on; title('Nyquist fs=30Hz');\n"
            "subplot(3,1,3); plot(tc, xc, 'k--', t3, x3, 'g-o'); grid on; title('Over-sampled fs=150Hz');\n"
            "disp('Nyquist sampling theorem verified.');\n"
        ),
        "expected_output": "Nyquist sampling theorem simulation completed.",
        "viva_questions_json": [
            {"question": "What is the Nyquist rate for a signal x(t) = 5 cos(100 pi t) + 2 sin(300 pi t)?", "answer": "The highest frequency component is f_max = 300 pi / (2 pi) = 150 Hz. Therefore, the Nyquist rate is 2 * f_max = 300 Hz."},
            {"question": "What mathematical function acts as the ideal reconstruction interpolation filter?", "answer": "The ideal low-pass interpolation filter in the time domain is the sinc(t/Ts) function."}
        ]
    },

    # 6. Aliasing
    {
        "category_code": "DSP",
        "title": "Analysis of Frequency Aliasing Effect",
        "slug": "aliasing-effect",
        "objective": "To demonstrate the fold-over of high frequency spectral components into false lower frequencies during under-sampling.",
        "theory": (
            "When a signal with frequency f_in is sampled at a rate fs < 2*f_in, the high frequency spectral component "
            "aliases into an apparent frequency f_alias = |f_in - k*fs|. In audio and image processing, aliasing produces "
            "audible distortion and Moiré visual patterns."
        ),
        "equations_json": [
            "f_{\\text{alias}} = |f_{\\text{in}} - k f_s| \\le \\frac{f_s}{2}",
            "f_{\\text{apparent}} = |f_{\\text{in}} - f_s|"
        ],
        "procedure_json": [
            "Select high frequency test signal at fin = 85 Hz",
            "Set sampling frequency fs = 100 Hz (Nyquist requires fs > 170 Hz)",
            "Compute the expected alias frequency f_alias = |85 - 100| = 15 Hz",
            "Plot the true 85 Hz wave, discrete sample points, and the apparent 15 Hz reconstructed curve"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "fin = 85.0        # 85 Hz input signal\n"
            "fs = 100.0        # 100 Hz sampling rate (Nyquist rate = 170 Hz -> Under-sampled!)\n"
            "f_alias = np.abs(fin - fs)  # Expected alias = 15 Hz\n\n"
            "t_fine = np.linspace(0, 0.1, 1000)\n"
            "x_true = np.sin(2 * np.pi * fin * t_fine)\n\n"
            "t_samples = np.arange(0, 0.1, 1/fs)\n"
            "x_samples = np.sin(2 * np.pi * fin * t_samples)\n\n"
            "x_aliased_recon = np.sin(2 * np.pi * (-f_alias) * t_fine)\n\n"
            "plt.figure(figsize=(9, 5))\n"
            "plt.plot(t_fine, x_true, 'k--', label=f'True Signal ({fin} Hz)', alpha=0.5)\n"
            "plt.plot(t_fine, -x_aliased_recon, 'r-', lw=2, label=f'Apparent Aliased Signal ({f_alias} Hz)')\n"
            "plt.stem(t_samples, x_samples, linefmt='b-', markerfmt='bo', basefmt='k-', label='Sample Points (fs = 100 Hz)')\n"
            "plt.title(f'Aliasing Demonstration: 85 Hz Signal Sampled at 100 Hz Appears as {f_alias} Hz')\n"
            "plt.xlabel('Time (s)'); plt.ylabel('Amplitude')\n"
            "plt.grid(True); plt.legend()\n"
            "print(f'Actual Frequency: {fin} Hz | Apparent Alias Frequency: {f_alias} Hz')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "fin = 85.0; fs = 100.0; f_alias = abs(fin - fs)\n"
            "t = np.linspace(0, 0.1, 1000); x_true = np.sin(2*np.pi*fin*t)\n"
            "ts = np.arange(0, 0.1, 1/fs); xs = np.sin(2*np.pi*fin*ts)\n"
            "plt.plot(t, x_true, 'k--', label=f'{fin}Hz True'); plt.stem(ts, xs, 'b', label='Samples')\n"
            "plt.plot(t, np.sin(2*np.pi*f_alias*t), 'r', label=f'{f_alias}Hz Alias')\n"
            "plt.legend(); plt.grid(True); plt.title('Aliasing Effect')\n"
            "print(f'Alias frequency: {f_alias} Hz')\n"
        ),
        "matlab_code": (
            "% Aliasing Demonstration\n"
            "clear all; close all; clc;\n"
            "fin = 85; fs = 100; f_alias = abs(fin - fs);\n"
            "t = 0:0.0001:0.1; xt = sin(2*pi*fin*t);\n"
            "ts = 0:1/fs:0.1; xs = sin(2*pi*fin*ts);\n"
            "figure(1);\n"
            "plot(t, xt, 'k--'); hold on;\n"
            "stem(ts, xs, 'b', 'filled');\n"
            "plot(t, sin(2*pi*f_alias*t), 'r-', 'LineWidth', 1.5); hold off;\n"
            "grid on; title('Aliasing: 85 Hz sampled at 100 Hz appears as 15 Hz');\n"
            "disp(['Apparent alias frequency: ', num2str(f_alias), ' Hz']);\n"
        ),
        "expected_output": "Actual Frequency: 85.0 Hz | Apparent Alias Frequency: 15.0 Hz",
        "viva_questions_json": [
            {"question": "How can aliasing be practically eliminated in hardware?", "answer": "By placing an analog low-pass Anti-Aliasing Filter (AAF) prior to the Analog-to-Digital Converter (ADC) to remove frequencies above fs/2."},
            {"question": "What is meant by the folding frequency?", "answer": "The folding frequency is fs/2 (the Nyquist limit); frequencies above fs/2 fold symmetrically back into the frequency interval [0, fs/2]."}
        ]
    },

    # 7. Linear Convolution
    {
        "category_code": "DSP",
        "title": "Linear Convolution of Discrete Sequences",
        "slug": "linear-convolution",
        "objective": "To compute and visualize the time-domain linear convolution of an input signal with an LTI impulse response.",
        "theory": (
            "Linear convolution calculates the forced response of an LTI system to any arbitrary input sequence x[n]. "
            "Mathematically, y[n] = x[n] * h[n] = sum_{k} x[k] * h[n-k]. "
            "If x[n] has length Lx and h[n] has length Lh, the convolved output sequence y[n] has length Ly = Lx + Lh - 1."
        ),
        "equations_json": [
            "y[n] = x[n] * h[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n-k]",
            "L_y = L_x + L_h - 1",
            "Y(z) = X(z) \\cdot H(z) \\text{ (Z-domain Multiplication)}"
        ],
        "procedure_json": [
            "Define discrete input sequence x = [1, 2, 3, 2, 1]",
            "Define FIR impulse response h = [1, 1, 1] (moving average)",
            "Compute linear convolution via np.convolve() or conv()",
            "Plot x[n], h[n], and resulting y[n] on aligned stem plots"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "x = np.array([1, 2, 3, 2, 1])\n"
            "h = np.array([1, 1, 1])\n\n"
            "y = np.convolve(x, h)\n\n"
            "nx = np.arange(len(x))\n"
            "nh = np.arange(len(h))\n"
            "ny = np.arange(len(y))\n\n"
            "fig, axs = plt.subplots(3, 1, figsize=(8, 6))\n"
            "axs[0].stem(nx, x, linefmt='b-', markerfmt='bo', basefmt='k-')\n"
            "axs[0].set_title(f'Input Sequence x[n] (Length {len(x)})'); axs[0].grid(True)\n\n"
            "axs[1].stem(nh, h, linefmt='m-', markerfmt='mo', basefmt='k-')\n"
            "axs[1].set_title(f'Impulse Response h[n] (Length {len(h)})'); axs[1].grid(True)\n\n"
            "axs[2].stem(ny, y, linefmt='r-', markerfmt='ro', basefmt='k-')\n"
            "axs[2].set_title(f'Linear Convolution y[n] = x[n]*h[n] (Length {len(y)})')\n"
            "axs[2].set_xlabel('Sample Index n'); axs[2].grid(True)\n\n"
            "plt.tight_layout()\n"
            "print('Input x:', x.tolist())\n"
            "print('Impulse h:', h.tolist())\n"
            "print('Convolution y:', y.tolist())\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "x = np.array([1, 2, 3, 2, 1]); h = np.array([1, 1, 1]); y = np.convolve(x, h)\n"
            "plt.figure(figsize=(7, 3))\n"
            "plt.stem(range(len(y)), y, 'r'); plt.title('Linear Convolution'); plt.grid(True)\n"
            "print('y =', y.tolist())\n"
        ),
        "matlab_code": (
            "% Linear Convolution\n"
            "clear all; close all; clc;\n"
            "x = [1, 2, 3, 2, 1]; h = [1, 1, 1];\n"
            "y = conv(x, h);\n"
            "figure(1); stem(0:length(y)-1, y, 'r', 'filled'); grid on; title('Linear Convolution');\n"
            "disp('Convolution result y:'); disp(y);\n"
        ),
        "expected_output": "Convolution y: [1, 3, 6, 7, 6, 3, 1]",
        "viva_questions_json": [
            {"question": "What is the computational complexity of direct linear convolution for sequences of length N?", "answer": "The direct convolution sum requires O(N^2) multiply-accumulate operations."},
            {"question": "How can convolution of long signals be computed efficiently?", "answer": "Using Fast Convolution algorithms via the Fast Fourier Transform (Overlap-Add or Overlap-Save methods) in O(N log N) time."}
        ]
    },

    # 8. Circular Convolution
    {
        "category_code": "DSP",
        "title": "Circular Convolution and Modulo-N Indexing",
        "slug": "circular-convolution",
        "objective": "To perform modulo-N circular convolution and compare it with zero-padded linear convolution.",
        "theory": (
            "Circular convolution evaluates the convolution of two N-point periodic sequences over one period: "
            "y_c[n] = sum_{k=0}^{N-1} x[k] h[((n-k))_N]. By the DFT Convolution Property, circular convolution "
            "in the time domain corresponds to exact pointwise multiplication of their discrete Fourier spectra: Y[k] = X[k] * H[k]."
        ),
        "equations_json": [
            "y_{\\text{circ}}[n] = \\sum_{k=0}^{N-1} x[k] h[((n-k))_N]",
            "Y[k] = \\text{DFT}\\{y_{\\text{circ}}[n]\\} = X[k] \\cdot H[k]",
            "y_{\\text{circ}}[n] = \\text{IDFT}\\{X[k] \\cdot H[k]\\}"
        ],
        "procedure_json": [
            "Define two 4-point sequences x = [1, 2, 3, 4] and h = [1, 1, 1, 1]",
            "Compute 4-point circular convolution via IDFT(DFT(x) * DFT(h))",
            "Zero-pad to N = 7 to obtain linear convolution via circular convolution",
            "Plot circular vs linear convolution results"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "x = np.array([1, 2, 3, 4])\n"
            "h = np.array([1, 1, 1, 1])\n"
            "N = max(len(x), len(h))\n\n"
            "# 1. Direct Circular Convolution via DFT\n"
            "X = np.fft.fft(x, N)\n"
            "H = np.fft.fft(h, N)\n"
            "y_circ = np.round(np.real(np.fft.ifft(X * H)))\n\n"
            "# 2. Linear Convolution via Zero-Padding (N_lin = 4 + 4 - 1 = 7)\n"
            "N_lin = len(x) + len(h) - 1\n"
            "X_pad = np.fft.fft(x, N_lin)\n"
            "H_pad = np.fft.fft(h, N_lin)\n"
            "y_lin = np.round(np.real(np.fft.ifft(X_pad * H_pad)))\n\n"
            "fig, axs = plt.subplots(2, 1, figsize=(8, 5))\n"
            "axs[0].stem(range(N), y_circ, linefmt='b-', markerfmt='bo')\n"
            "axs[0].set_title(f'4-Point Circular Convolution y_c[n] = {y_circ.astype(int).tolist()}'); axs[0].grid(True)\n\n"
            "axs[1].stem(range(N_lin), y_lin, linefmt='r-', markerfmt='ro')\n"
            "axs[1].set_title(f'7-Point Linear Convolution (Zero-Padded) y_l[n] = {y_lin.astype(int).tolist()}'); axs[1].grid(True)\n"
            "axs[1].set_xlabel('Sample Index n')\n\n"
            "plt.tight_layout()\n"
            "print('Circular Convolution Result:', y_circ.astype(int).tolist())\n"
            "print('Linear Convolution Result:', y_lin.astype(int).tolist())\n"
        ),
        "python_code": (
            "import numpy as np\n"
            "x = np.array([1, 2, 3, 4]); h = np.array([1, 1, 1, 1]); N = 4\n"
            "y_circ = np.round(np.real(np.fft.ifft(np.fft.fft(x)*np.fft.fft(h)))).astype(int)\n"
            "print('Circular conv:', y_circ.tolist())\n"
        ),
        "matlab_code": (
            "% Circular Convolution\n"
            "clear all; close all; clc;\n"
            "x = [1, 2, 3, 4]; h = [1, 1, 1, 1];\n"
            "y_circ = cconv(x, h, 4);\n"
            "disp('Circular convolution:'); disp(y_circ);\n"
        ),
        "expected_output": "Circular Convolution Result: [10, 10, 10, 10]",
        "viva_questions_json": [
            {"question": "What minimum padding length is required for circular convolution to match linear convolution?", "answer": "The sequences must be zero-padded to at least N >= L1 + L2 - 1 points."},
            {"question": "Why does circular convolution exhibit time-domain aliasing when N < L1 + L2 - 1?", "answer": "Because the tail terms wrap around modulo N and add back into the beginning of the sequence."}
        ]
    },

    # 9. Cross-Correlation
    {
        "category_code": "DSP",
        "title": "Cross-Correlation for Time Delay Estimation",
        "slug": "cross-correlation",
        "objective": "To measure the similarity and estimate the propagation delay between two signals using cross-correlation.",
        "theory": (
            "Cross-correlation r_xy[m] measures the degree of linear dependence and relative time lag m between two signals: "
            "r_xy[m] = sum_n x[n] * y[n-m]. The lag m_max where r_xy[m] achieves its global maximum precisely indicates the time delay."
        ),
        "equations_json": [
            "r_{xy}[m] = \\sum_{n=-\\infty}^{\\infty} x[n] y[n-m]",
            "\\text{Delay } \\tau = \\arg\\max_m \\{ r_{xy}[m] \\} \\cdot T_s"
        ],
        "procedure_json": [
            "Generate source pulse x[n]",
            "Create delayed noisy received signal y[n] with deliberate delay of 8 samples",
            "Compute cross-correlation sequence using np.correlate()",
            "Detect peak lag index and confirm estimated delay matches 8 samples"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "# 1. Transmitted Radar Pulse\n"
            "np.random.seed(42)\n"
            "tx_pulse = np.sin(2 * np.pi * 0.1 * np.arange(20)) * np.hanning(20)\n\n"
            "# 2. Received Signal (Delayed by 8 samples + Gaussian Noise)\n"
            "delay_actual = 8\n"
            "rx_signal = np.zeros(60)\n"
            "rx_signal[delay_actual:delay_actual + len(tx_pulse)] = tx_pulse\n"
            "rx_signal += 0.15 * np.random.randn(len(rx_signal))\n\n"
            "# 3. Cross-correlation\n"
            "xcorr = np.correlate(rx_signal, tx_pulse, mode='full')\n"
            "lags = np.arange(-len(tx_pulse) + 1, len(rx_signal))\n"
            "detected_lag = lags[np.argmax(xcorr)]\n\n"
            "plt.figure(figsize=(9, 6))\n"
            "plt.subplot(3, 1, 1)\n"
            "plt.stem(tx_pulse, linefmt='b-', markerfmt='bo'); plt.title('Transmitted Pulse x[n]'); plt.grid(True)\n\n"
            "plt.subplot(3, 1, 2)\n"
            "plt.plot(rx_signal, 'r-o', lw=1.2); plt.title(f'Received Noisy Signal y[n] (True Delay = {delay_actual})'); plt.grid(True)\n\n"
            "plt.subplot(3, 1, 3)\n"
            "plt.plot(lags, xcorr, 'g-', lw=1.8)\n"
            "plt.axvline(detected_lag, color='k', linestyle='--', label=f'Peak Lag = {detected_lag}')\n"
            "plt.title('Cross-Correlation r_{yx}[m] (Peak corresponds to estimated delay)')\n"
            "plt.xlabel('Lag Index m'); plt.grid(True); plt.legend()\n"
            "plt.tight_layout()\n"
            "print(f'Actual Delay: {delay_actual} samples | Detected Lag: {detected_lag} samples')\n"
        ),
        "python_code": (
            "import numpy as np\n"
            "x = np.sin(np.linspace(0, np.pi, 10))\n"
            "y = np.pad(x, (5, 0)) # delay 5\n"
            "corr = np.correlate(y, x, 'full')\n"
            "lag = np.argmax(corr) - (len(x) - 1)\n"
            "print('Estimated lag:', lag)\n"
        ),
        "matlab_code": (
            "% Cross-Correlation\n"
            "clear all; close all; clc;\n"
            "x = sin(linspace(0, pi, 10)); y = [zeros(1, 5), x];\n"
            "[c, lags] = xcorr(y, x);\n"
            "[~, idx] = max(c); est_lag = lags(idx);\n"
            "disp(['Estimated delay: ', num2str(est_lag)]);\n"
        ),
        "expected_output": "Actual Delay: 8 samples | Detected Lag: 8 samples",
        "viva_questions_json": [
            {"question": "Does cross-correlation satisfy commutative property r_xy[m] = r_yx[m]?", "answer": "No. Cross-correlation satisfies conjugate-symmetric time-reversal: r_xy[m] = r_yx[-m]."},
            {"question": "How is cross-correlation utilized in GPS receivers?", "answer": "GPS receivers correlate the incoming satellite signal with replica PRN (pseudorandom noise) Gold codes to acquire lock and determine code phase delay."}
        ]
    },

    # 10. Autocorrelation
    {
        "category_code": "DSP",
        "title": "Autocorrelation of Deterministic & Random Signals",
        "slug": "autocorrelation",
        "objective": "To calculate the autocorrelation sequence r_xx[m] of periodic signals and random white noise, demonstrating periodicity extraction.",
        "theory": (
            "Autocorrelation evaluates the correlation of a signal with a delayed version of itself: "
            "r_xx[m] = sum_n x[n] * x[n-m]. For periodic signals with period N0, r_xx[m] is strictly periodic with identical period N0. "
            "For white noise, r_xx[m] collapses to a delta spike at zero lag m = 0, proving zero correlation across distinct time instances."
        ),
        "equations_json": [
            "r_{xx}[m] = \\sum_{n=-\\infty}^{\\infty} x[n] x[n-m]",
            "r_{xx}[0] = E_x = \\sum_{n} |x[n]|^2 \\text{ (Total Energy)}",
            "|r_{xx}[m]| \\le r_{xx}[0] \\quad \\forall m"
        ],
        "procedure_json": [
            "Generate periodic sine wave buried in high-amplitude zero-mean Gaussian white noise",
            "Compute autocorrelation using np.correlate(mode='full')",
            "Observe the recovery of periodic sinusoidal variation in r_xx[m] despite noisy time waveform",
            "Verify that the global maximum occurs at m = 0"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "np.random.seed(42)\n"
            "fs = 100.0\n"
            "t = np.arange(0, 1.0, 1/fs)\n"
            "clean_signal = np.sin(2 * np.pi * 5.0 * t)  # 5 Hz sinusoid (Period = 20 samples)\n"
            "noise = 1.5 * np.random.randn(len(t))\n"
            "noisy_signal = clean_signal + noise\n\n"
            "# Autocorrelation of noisy signal\n"
            "rxx = np.correlate(noisy_signal, noisy_signal, mode='full')\n"
            "lags = np.arange(-len(t) + 1, len(t))\n\n"
            "plt.figure(figsize=(9, 6))\n"
            "plt.subplot(2, 1, 1)\n"
            "plt.plot(t, noisy_signal, 'k-', lw=1.2)\n"
            "plt.title('Sinusoid Buried in Noise (SNR < 0 dB)')\n"
            "plt.xlabel('Time (s)'); plt.grid(True)\n\n"
            "plt.subplot(2, 1, 2)\n"
            "plt.plot(lags, rxx, 'b-', lw=1.5)\n"
            "plt.axvline(0, color='r', linestyle='--', label='Zero Lag (Energy Peak)')\n"
            "plt.title('Autocorrelation Sequence r_{xx}[m] (Reveals True 5 Hz Periodicity)')\n"
            "plt.xlabel('Lag m'); plt.grid(True); plt.legend()\n"
            "plt.tight_layout()\n"
            "print(f'Max autocorrelation at zero lag: {rxx[len(t)-1]:.2f}')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "t = np.linspace(0, 1, 100); x = np.sin(2*np.pi*5*t) + 0.5*np.random.randn(100)\n"
            "rxx = np.correlate(x, x, 'full')\n"
            "print('Zero lag energy:', rxx[len(x)-1])\n"
        ),
        "matlab_code": (
            "% Autocorrelation\n"
            "clear all; close all; clc;\n"
            "t = 0:0.01:1; x = sin(2*pi*5*t) + 0.5*randn(size(t));\n"
            "[rxx, lags] = xcorr(x);\n"
            "figure(1); plot(lags, rxx); grid on; title('Autocorrelation');\n"
            "disp(['Zero lag value: ', num2str(rxx(length(t)))]);\n"
        ),
        "expected_output": "Max autocorrelation at zero lag:",
        "viva_questions_json": [
            {"question": "State the Wiener-Khinchin theorem.", "answer": "The Wiener-Khinchin theorem states that the Power Spectral Density (PSD) of a wide-sense stationary random process is the Fourier transform of its autocorrelation function."},
            {"question": "What does r_xx[0] represent physically for a zero-mean electrical signal?", "answer": "It represents the total average signal energy (or average signal power for a power signal)."}
        ]
    },

    # 11. Fourier Series
    {
        "category_code": "DSP",
        "title": "Fourier Series Synthesis of Periodic Waveforms",
        "slug": "fourier-series",
        "objective": "To reconstruct periodic square waveforms from harmonic components and observe the Gibbs overshoot phenomenon.",
        "theory": (
            "Any periodic signal satisfying Dirichlet conditions can be decomposed into an infinite sum of harmonically related sines and cosines. "
            "For an odd square wave of period T0: x(t) = (4/pi) * sum_{k=1,3,5...} (1/k) * sin(k * omega_0 * t). "
            "Truncating to N terms produces high-frequency ripple near discontinuities with an 8.95% persistent overshoot known as the Gibbs phenomenon."
        ),
        "equations_json": [
            "x(t) = a_0 + \\sum_{k=1}^{\\infty} \\left[ a_k \\cos(k \\omega_0 t) + b_k \\sin(k \\omega_0 t) \\right]",
            "x_{\\text{square}}(t) = \\frac{4}{\\pi} \\sum_{n=1,3,5\\dots}^{N} \\frac{1}{n} \\sin(n \\omega_0 t)",
            "\\text{Gibbs Overshoot} \\approx 8.95\\% \\text{ at step discontinuities}"
        ],
        "procedure_json": [
            "Define fundamental frequency f0 = 2 Hz over one period",
            "Synthesize approximations summing 1, 3, 9, and 49 odd harmonic terms",
            "Plot harmonic approximations overlaid to observe convergence and ripple near edges"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "f0 = 2.0\n"
            "t = np.linspace(-0.5, 0.5, 1000)\n"
            "omega0 = 2 * np.pi * f0\n\n"
            "def fourier_square(t, N_harmonics):\n"
            "    val = np.zeros_like(t)\n"
            "    for k in range(1, N_harmonics + 1, 2):\n"
            "        val += (4.0 / (np.pi * k)) * np.sin(k * omega0 * t)\n"
            "    return val\n\n"
            "plt.figure(figsize=(9, 6))\n"
            "for n_terms, color in [(1, 'g'), (3, 'b'), (9, 'm'), (49, 'r')]:\n"
            "    plt.plot(t, fourier_square(t, n_terms), color, label=f'N = {n_terms} Harmonics')\n\n"
            "plt.title('Fourier Series Approximation of a Square Wave (Gibbs Phenomenon)')\n"
            "plt.xlabel('Time (s)'); plt.ylabel('Amplitude')\n"
            "plt.grid(True); plt.legend()\n"
            "print('Fourier series synthesis completed for N=[1, 3, 9, 49].')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "t = np.linspace(0, 1, 500); sq = sum((4/(np.pi*k))*np.sin(2*np.pi*k*t) for k in range(1, 15, 2))\n"
            "plt.plot(t, sq); plt.title('Fourier Square Wave'); plt.grid(True)\n"
            "print('Fourier synthesis complete.')\n"
        ),
        "matlab_code": (
            "% Fourier Series Synthesis\n"
            "clear all; close all; clc;\n"
            "t = 0:0.002:1; sq = zeros(size(t));\n"
            "for k = 1:2:15\n"
            "    sq = sq + (4/(pi*k)) * sin(2*pi*k*t);\n"
            "end\n"
            "figure(1); plot(t, sq); grid on; title('Fourier Series');\n"
            "disp('Fourier synthesis complete.');\n"
        ),
        "expected_output": "Fourier series synthesis completed for N=[1, 3, 9, 49].",
        "viva_questions_json": [
            {"question": "What are the Dirichlet conditions for Fourier series existence?", "answer": "1. x(t) must be absolutely integrable over one period. 2. x(t) has a finite number of maxima and minima in any period. 3. x(t) has a finite number of finite discontinuities in any period."},
            {"question": "Does increasing the number of harmonics N to infinity eliminate the Gibbs overshoot amplitude?", "answer": "No. The overshoot width shrinks toward zero, but its peak amplitude remains approximately 8.95% above the true discontinuity level."}
        ]
    },

    # 12. Fourier Transform
    {
        "category_code": "DSP",
        "title": "Continuous-Time & Discrete-Time Fourier Transform",
        "slug": "fourier-transform",
        "objective": "To evaluate and plot the continuous spectral magnitude and phase of an aperiodic rectangular pulse.",
        "theory": (
            "The Fourier Transform maps continuous aperiodic time-domain signals to the continuous frequency domain: "
            "X(f) = int_{-inf}^{inf} x(t) * exp(-j*2*pi*f*t) dt. "
            "For a symmetric rectangular pulse of width tau: x(t) = rect(t/tau) <-> X(f) = tau * sinc(f * tau)."
        ),
        "equations_json": [
            "X(f) = \\int_{-\\infty}^{\\infty} x(t) e^{-j 2\\pi f t} dt",
            "x(t) = \\text{rect}(t/\\tau) \\longleftrightarrow X(f) = \\tau \\cdot \\text{sinc}(f\\tau) = \\tau \\frac{\\sin(\\pi f \\tau)}{\\pi f \\tau}"
        ],
        "procedure_json": [
            "Define pulse duration tau = 0.2 s and frequency span f from -25 to +25 Hz",
            "Evaluate analytical Sinc spectrum",
            "Plot magnitude spectrum |X(f)| showing main lobe and side lobes with zero-crossings at multiples of 1/tau"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "tau = 0.2         # Pulse width = 0.2s\n"
            "f = np.linspace(-30, 30, 1000)\n"
            "X_f = tau * np.sinc(f * tau)  # numpy sinc(x) is sin(pi*x)/(pi*x)\n\n"
            "plt.figure(figsize=(9, 5))\n"
            "plt.plot(f, np.abs(X_f), 'b-', lw=2, label='Magnitude |X(f)| = \\tau |sinc(f \\tau)|')\n"
            "plt.plot(f, X_f, 'r--', lw=1.2, label='Real Amplitude Spectrum X(f)', alpha=0.7)\n"
            "plt.axvline(1/tau, color='k', linestyle=':', label=f'First Zero = 1/\\tau = {1/tau:.1f} Hz')\n"
            "plt.axvline(-1/tau, color='k', linestyle=':')\n"
            "plt.title(f'Continuous Fourier Transform of Rectangular Pulse (\\tau = {tau}s)')\n"
            "plt.xlabel('Frequency (Hz)'); plt.ylabel('Spectral Density (V/Hz)')\n"
            "plt.grid(True); plt.legend()\n"
            "print(f'Main lobe width: {2/tau:.1f} Hz')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "tau = 0.2; f = np.linspace(-30, 30, 1000); X = tau * np.sinc(f * tau)\n"
            "plt.plot(f, np.abs(X)); plt.grid(True); plt.title('Sinc Spectrum')\n"
            "print('Mainlobe width:', 2/tau)\n"
        ),
        "matlab_code": (
            "% Fourier Transform of Rectangular Pulse\n"
            "clear all; close all; clc;\n"
            "tau = 0.2; f = -30:0.05:30; X = tau * sinc(f * tau);\n"
            "figure(1); plot(f, abs(X), 'b', 'LineWidth', 1.5); grid on; title('Rect Pulse Spectrum');\n"
            "disp(['Mainlobe width: ', num2str(2/tau), ' Hz']);\n"
        ),
        "expected_output": "Main lobe width: 10.0 Hz",
        "viva_questions_json": [
            {"question": "What is the duality property of the Fourier Transform?", "answer": "If x(t) <-> X(f), then X(t) <-> x(-f). For instance, a rectangular pulse in time has a sinc spectrum in frequency, and a sinc signal in time has a rectangular spectrum in frequency."},
            {"question": "What happens to the Fourier spectrum when a time signal is compressed by factor a (x(at))?", "answer": "By the time scaling theorem: x(at) <-> (1/|a|) * X(f/a). Time compression leads to frequency expansion, illustrating the fundamental uncertainty principle."}
        ]
    },

    # 13. FFT and IFFT
    {
        "category_code": "DSP",
        "title": "Fast Fourier Transform (FFT) and Inverse FFT",
        "slug": "fft-ifft",
        "objective": "To compute the frequency spectrum using the Cooley-Tukey Radix-2 FFT algorithm and recover the exact time signal using IFFT.",
        "theory": (
            "The Discrete Fourier Transform (DFT) maps N time samples to N frequency bins: X[k] = sum_{n=0}^{N-1} x[n] W_N^{nk}. "
            "Direct DFT requires N^2 complex operations. The Radix-2 Fast Fourier Transform (FFT) uses divide-and-conquer symmetry "
            "to compute the exact DFT in only (N/2) * log2(N) operations."
        ),
        "equations_json": [
            "X[k] = \\sum_{n=0}^{N-1} x[n] e^{-j 2\\pi n k / N}, \\quad k = 0, 1, \\dots, N-1",
            "x[n] = \\frac{1}{N} \\sum_{k=0}^{N-1} X[k] e^{j 2\\pi n k / N} \\text{ (IFFT)}",
            "\\text{Speedup} = \\frac{N^2}{N \\log_2 N} = \\frac{N}{\\log_2 N}"
        ],
        "procedure_json": [
            "Synthesize composite multi-tone signal x(t) = sin(2*pi*50*t) + 0.5*sin(2*pi*120*t)",
            "Sample at fs = 1000 Hz with N = 1024 points",
            "Compute two-sided and single-sided FFT amplitude spectra",
            "Apply inverse FFT (np.fft.ifft) and confirm maximum reconstruction error is near machine epsilon"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 1000.0       # Sampling rate 1 kHz\n"
            "N = 1024          # Power of 2 for optimal radix-2 FFT\n"
            "t = np.arange(N) / fs\n\n"
            "# Multi-tone signal: 50 Hz and 120 Hz\n"
            "x = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)\n\n"
            "# 1. Compute FFT\n"
            "X = np.fft.fft(x)\n"
            "freqs = np.fft.fftfreq(N, 1/fs)\n"
            "magnitude = (2.0 / N) * np.abs(X[:N//2])\n"
            "f_positive = freqs[:N//2]\n\n"
            "# 2. Reconstruct via IFFT\n"
            "x_recon = np.real(np.fft.ifft(X))\n"
            "max_error = np.max(np.abs(x - x_recon))\n\n"
            "fig, axs = plt.subplots(2, 1, figsize=(9, 6))\n"
            "axs[0].plot(t[:100], x[:100], 'b-', label='Original Signal x(t)')\n"
            "axs[0].set_title('Time Domain Signal (First 100 ms)'); axs[0].set_xlabel('Time (s)'); axs[0].grid(True)\n\n"
            "axs[1].plot(f_positive, magnitude, 'r-', lw=1.5)\n"
            "axs[1].set_title('Single-Sided FFT Amplitude Spectrum (Peaks at 50 Hz and 120 Hz)')\n"
            "axs[1].set_xlabel('Frequency (Hz)'); axs[1].set_ylabel('Amplitude (V)'); axs[1].set_xlim(0, 200); axs[1].grid(True)\n"
            "plt.tight_layout()\n"
            "print(f'FFT computed for N = {N} points.')\n"
            "print(f'Max IFFT Reconstruction Error: {max_error:.2e}')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "fs = 1000; t = np.arange(512)/fs; x = np.sin(2*np.pi*50*t) + 0.5*sin(2*np.pi*120*t)\n"
            "X = np.fft.fft(x); f = np.fft.fftfreq(len(x), 1/fs)\n"
            "plt.plot(f[:256], np.abs(X[:256])); plt.grid(True); plt.title('FFT Spectrum')\n"
            "print('FFT completed.')\n"
        ),
        "matlab_code": (
            "% Fast Fourier Transform (FFT)\n"
            "clear all; close all; clc;\n"
            "fs = 1000; N = 1024; t = (0:N-1)/fs;\n"
            "x = sin(2*pi*50*t) + 0.5*sin(2*pi*120*t);\n"
            "X = fft(x); f = (0:N/2-1)*(fs/N);\n"
            "figure(1); plot(f, (2/N)*abs(X(1:N/2)), 'r'); grid on; title('FFT Spectrum');\n"
            "disp('FFT execution completed.');\n"
        ),
        "expected_output": "FFT computed for N = 1024 points.",
        "viva_questions_json": [
            {"question": "How many multiplications does a 1024-point Radix-2 FFT require compared to direct DFT?", "answer": "Direct DFT requires N^2 = 1,048,576 operations. Radix-2 FFT requires (N/2)*log2(N) = 512 * 10 = 5,120 complex multiplications, which is over 200 times faster."},
            {"question": "What is the Twiddle factor W_N in FFT?", "answer": "W_N = exp(-j * 2*pi / N); it represents the primitive N-th root of unity and possesses symmetry (W_N^{k + N/2} = -W_N^k) and periodicity (W_N^{k+N} = W_N^k)."}
        ]
    },

    # 14. FIR Filter Design
    {
        "category_code": "DSP",
        "title": "FIR Low-Pass Filter Design via Windowing",
        "slug": "fir-filter-design",
        "objective": "To design a linear-phase Finite Impulse Response (FIR) low-pass filter using Hamming, Hanning, and Blackman windows.",
        "theory": (
            "FIR filters possess inherently guaranteed bounded-input bounded-output (BIBO) stability and exact linear phase. "
            "The window method truncates the infinite sinc impulse response of an ideal filter using a tapered finite window w[n]: "
            "h[n] = h_ideal[n] * w[n]. The Hamming window achieves -53 dB stopband attenuation."
        ),
        "equations_json": [
            "h_d[n] = \\frac{\\sin(\\omega_c (n - M))}{\\pi (n - M)}, \\quad M = \\frac{N-1}{2}",
            "w_{\\text{Hamming}}[n] = 0.54 - 0.46 \\cos\\left(\\frac{2\\pi n}{N-1}\\right)",
            "w_{\\text{Hanning}}[n] = 0.5 - 0.5 \\cos\\left(\\frac{2\\pi n}{N-1}\\right)"
        ],
        "procedure_json": [
            "Specify filter order N = 51 (odd) and cutoff frequency fc = 1500 Hz for fs = 8000 Hz",
            "Generate ideal impulse response hd[n]",
            "Apply Hamming window to calculate causal filter taps h[n]",
            "Compute and plot magnitude frequency response in decibels (dB)"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import scipy.signal as signal\n"
            "import matplotlib.pyplot as plt\n\n"
            "N = 51            # Filter taps (order 50)\n"
            "fc = 1500.0       # Cutoff 1.5 kHz\n"
            "fs = 8000.0       # Sampling rate 8 kHz\n\n"
            "# 1. Design FIR filter using Hamming window\n"
            "h_hamming = signal.firwin(N, cutoff=fc, fs=fs, window='hamming')\n"
            "h_hanning = signal.firwin(N, cutoff=fc, fs=fs, window='hann')\n\n"
            "# 2. Frequency response\n"
            "w, H_ham = signal.freqz(h_hamming, worN=1024, fs=fs)\n"
            "_, H_han = signal.freqz(h_hanning, worN=1024, fs=fs)\n\n"
            "plt.figure(figsize=(9, 6))\n"
            "plt.subplot(2, 1, 1)\n"
            "plt.plot(w, 20 * np.log10(np.abs(H_ham)), 'b-', lw=1.8, label='Hamming (Stopband ~ -53 dB)')\n"
            "plt.plot(w, 20 * np.log10(np.abs(H_han)), 'r--', lw=1.5, label='Hanning (Stopband ~ -44 dB)')\n"
            "plt.axvline(fc, color='k', linestyle=':', label=f'Cutoff {fc} Hz')\n"
            "plt.title('FIR Low-Pass Filter Magnitude Response (dB)')\n"
            "plt.xlabel('Frequency (Hz)'); plt.ylabel('Magnitude (dB)')\n"
            "plt.ylim(-80, 5); plt.grid(True); plt.legend()\n\n"
            "plt.subplot(2, 1, 2)\n"
            "plt.stem(h_hamming, linefmt='b-', markerfmt='bo')\n"
            "plt.title(f'Symmetric Linear-Phase Impulse Response h[n] ({N} Taps)')\n"
            "plt.xlabel('Tap Index n'); plt.grid(True)\n"
            "plt.tight_layout()\n"
            "print(f'FIR filter design complete: {N} taps, cutoff {fc} Hz.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport scipy.signal as signal\nimport matplotlib.pyplot as plt\n"
            "h = signal.firwin(51, 1500, fs=8000, window='hamming')\n"
            "w, H = signal.freqz(h, fs=8000)\n"
            "plt.plot(w, 20*np.log10(np.abs(H))); plt.grid(True); plt.title('FIR Filter')\n"
            "print('FIR Filter Designed successfully.')\n"
        ),
        "matlab_code": (
            "% FIR Filter Design\n"
            "clear all; close all; clc;\n"
            "N = 51; fc = 1500; fs = 8000;\n"
            "h = fir1(N-1, fc/(fs/2), hamming(N));\n"
            "[H, f] = freqz(h, 1, 512, fs);\n"
            "figure(1); plot(f, 20*log10(abs(H))); grid on; title('FIR Magnitude Response');\n"
            "disp('FIR Filter Designed successfully.');\n"
        ),
        "expected_output": "FIR filter design complete: 51 taps, cutoff 1500.0 Hz.",
        "viva_questions_json": [
            {"question": "Why are FIR filters unconditionally stable?", "answer": "All poles of an FIR filter are located at the origin z = 0, which is strictly inside the unit circle |z| < 1."},
            {"question": "What is the condition for an FIR filter to exhibit strictly linear phase?", "answer": "The impulse response h[n] must possess even or odd symmetry about its midpoint: h[n] = +- h[N-1-n]."}
        ]
    },

    # 15. IIR Filter Design
    {
        "category_code": "DSP",
        "title": "IIR Butterworth Low-Pass Filter Design",
        "slug": "iir-filter-design",
        "objective": "To design an analog-derived Infinite Impulse Response (IIR) digital Butterworth filter via Bilinear Transformation.",
        "theory": (
            "IIR filters can achieve extremely sharp transition roll-offs with far fewer filter coefficients than FIR filters. "
            "The Butterworth response is characterized by a maximally flat magnitude in the passband with no equiripple ripple: "
            "|H(j*Omega)|^2 = 1 / (1 + (Omega / Omega_c)^(2N))."
        ),
        "equations_json": [
            "|H(j\\Omega)|^2 = \\frac{1}{1 + (\\Omega / \\Omega_c)^{2N}}",
            "s = \\frac{2}{T_s} \\frac{1 - z^{-1}}{1 + z^{-1}} \\text{ (Bilinear Transformation)}",
            "\\Omega = \\frac{2}{T_s} \\tan\\left(\\frac{\\omega}{2}\\right) \\text{ (Pre-warping)}"
        ],
        "procedure_json": [
            "Set passband edge fp = 1000 Hz and stopband edge fs = 1500 Hz for sampling rate 8000 Hz",
            "Specify passband ripple gpass = 1 dB and stopband attenuation gstop = 40 dB",
            "Determine minimum required order N using signal.buttord()",
            "Synthesize numerator b and denominator a polynomials using signal.butter()",
            "Plot magnitude frequency response and pole-zero constellation"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import scipy.signal as signal\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 8000.0       # Sampling rate\n"
            "wp = 1000.0       # Passband edge 1 kHz\n"
            "ws = 1600.0       # Stopband edge 1.6 kHz\n"
            "gpass = 1.0       # Max passband ripple 1 dB\n"
            "gstop = 40.0      # Min stopband attenuation 40 dB\n\n"
            "# 1. Calculate required Butterworth filter order\n"
            "N, Wn = signal.buttord(wp, ws, gpass, gstop, fs=fs)\n"
            "b, a = signal.butter(N, Wn, btype='low', fs=fs)\n\n"
            "# 2. Frequency Response\n"
            "w, H = signal.freqz(b, a, worN=1024, fs=fs)\n\n"
            "plt.figure(figsize=(9, 5))\n"
            "plt.plot(w, 20 * np.log10(np.abs(H)), 'b-', lw=2)\n"
            "plt.axvline(wp, color='g', linestyle='--', label=f'Passband {wp} Hz')\n"
            "plt.axvline(ws, color='r', linestyle='--', label=f'Stopband {ws} Hz')\n"
            "plt.axhline(-gpass, color='k', linestyle=':')\n"
            "plt.axhline(-gstop, color='k', linestyle=':')\n"
            "plt.title(f'Butterworth IIR Low-Pass Filter (Order N = {N})')\n"
            "plt.xlabel('Frequency (Hz)'); plt.ylabel('Magnitude (dB)')\n"
            "plt.ylim(-70, 5); plt.grid(True); plt.legend()\n"
            "print(f'Computed Butterworth Minimum Order: N = {N}')\n"
            "print('Numerator b:', np.round(b, 5).tolist())\n"
            "print('Denominator a:', np.round(a, 5).tolist())\n"
        ),
        "python_code": (
            "import numpy as np\nimport scipy.signal as signal\nimport matplotlib.pyplot as plt\n"
            "b, a = signal.butter(4, 1000, btype='low', fs=8000)\n"
            "w, H = signal.freqz(b, a, fs=8000)\n"
            "plt.plot(w, 20*np.log10(np.abs(H))); plt.grid(True); plt.title('IIR Butterworth')\n"
            "print('IIR filter design completed.')\n"
        ),
        "matlab_code": (
            "% IIR Butterworth Filter Design\n"
            "clear all; close all; clc;\n"
            "[b, a] = butter(4, 1000/(8000/2));\n"
            "[H, f] = freqz(b, a, 512, 8000);\n"
            "figure(1); plot(f, 20*log10(abs(H))); grid on; title('IIR Butterworth');\n"
            "disp('IIR filter design completed.');\n"
        ),
        "expected_output": "Computed Butterworth Minimum Order:",
        "viva_questions_json": [
            {"question": "Why is frequency pre-warping mandatory in the Bilinear Transformation?", "answer": "The non-linear tangent mapping between analog frequency Omega and digital frequency omega compresses analog frequencies up to infinity into [-pi, +pi], causing frequency distortion unless pre-warping is performed."},
            {"question": "Where must the poles of a causal, stable digital IIR filter reside?", "answer": "All poles must lie strictly inside the unit circle |z| < 1 in the complex z-plane."}
        ]
    },

    # 16. Low-pass and High-pass Filters
    {
        "category_code": "DSP",
        "title": "Low-Pass vs High-Pass Filter Comparison",
        "slug": "lowpass-highpass-filters",
        "objective": "To design and compare the dual frequency responses of complementary Low-Pass and High-Pass filters.",
        "theory": (
            "A high-pass filter can be directly derived from a low-pass filter by spectral inversion: "
            "H_HP(z) = 1 - H_LP(z), or in time domain: h_HP[n] = delta[n] - h_LP[n]. "
            "Low-pass filters pass DC and suppress high frequencies; high-pass filters block DC and preserve edges and transients."
        ),
        "equations_json": [
            "H_{\\text{HP}}(e^{j\\omega}) = 1 - H_{\\text{LP}}(e^{j\\omega})",
            "h_{\\text{HP}}[n] = \\delta[n - M] - h_{\\text{LP}}[n] \\text{ (Spectral Inversion)}"
        ],
        "procedure_json": [
            "Design a 5th-order Butterworth low-pass filter with cutoff fc = 1200 Hz at fs = 8000 Hz",
            "Design the corresponding 5th-order Butterworth high-pass filter with cutoff fc = 1200 Hz",
            "Compute frequency response of both filters",
            "Plot overlay showing complementary 3 dB intersection at 1200 Hz"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import scipy.signal as signal\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 8000.0\n"
            "fc = 1200.0\n"
            "order = 5\n\n"
            "b_lp, a_lp = signal.butter(order, fc, btype='low', fs=fs)\n"
            "b_hp, a_hp = signal.butter(order, fc, btype='high', fs=fs)\n\n"
            "w, H_lp = signal.freqz(b_lp, a_lp, worN=1024, fs=fs)\n"
            "_, H_hp = signal.freqz(b_hp, a_hp, worN=1024, fs=fs)\n\n"
            "plt.figure(figsize=(9, 5))\n"
            "plt.plot(w, 20 * np.log10(np.maximum(np.abs(H_lp), 1e-5)), 'b-', lw=2, label='Low-Pass Filter')\n"
            "plt.plot(w, 20 * np.log10(np.maximum(np.abs(H_hp), 1e-5)), 'r-', lw=2, label='High-Pass Filter')\n"
            "plt.axvline(fc, color='k', linestyle='--', label=f'Cutoff Frequency = {fc} Hz')\n"
            "plt.axhline(-3, color='k', linestyle=':', label='-3 dB Intersection')\n"
            "plt.title('Complementary Low-Pass & High-Pass Filter Responses')\n"
            "plt.xlabel('Frequency (Hz)'); plt.ylabel('Magnitude (dB)')\n"
            "plt.ylim(-60, 5); plt.grid(True); plt.legend()\n"
            "print(f'Low-pass & High-pass filters synthesized at fc = {fc} Hz.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport scipy.signal as signal\nimport matplotlib.pyplot as plt\n"
            "b_l, a_l = signal.butter(5, 1200, 'low', fs=8000)\n"
            "b_h, a_h = signal.butter(5, 1200, 'high', fs=8000)\n"
            "w, Hl = signal.freqz(b_l, a_l, fs=8000); _, Hh = signal.freqz(b_h, a_h, fs=8000)\n"
            "plt.plot(w, np.abs(Hl), 'b', label='LP'); plt.plot(w, np.abs(Hh), 'r', label='HP')\n"
            "plt.legend(); plt.grid(True); plt.title('LP vs HP Filter')\n"
            "print('LP and HP verified.')\n"
        ),
        "matlab_code": (
            "% Low-Pass vs High-Pass\n"
            "clear all; close all; clc;\n"
            "[bl, al] = butter(5, 1200/(8000/2), 'low');\n"
            "[bh, ah] = butter(5, 1200/(8000/2), 'high');\n"
            "[Hl, f] = freqz(bl, al, 512, 8000); [Hh, ~] = freqz(bh, ah, 512, 8000);\n"
            "figure(1); plot(f, abs(Hl), 'b', f, abs(Hh), 'r'); grid on;\n"
            "title('Low-Pass vs High-Pass'); legend('LP', 'HP');\n"
            "disp('LP and HP verified.');\n"
        ),
        "expected_output": "Low-pass & High-pass filters synthesized at fc = 1200.0 Hz.",
        "viva_questions_json": [
            {"question": "What is the spectral inversion relationship for FIR filters?", "answer": "For an odd-length linear-phase FIR lowpass filter, replacing h[n] with -h[n] and adding 1 to the center tap converts it into a highpass filter with cutoff pi - omega_c."},
            {"question": "What is the attenuation of a Butterworth filter at the cutoff frequency?", "answer": "The magnitude is exactly 1/sqrt(2) approx 0.7071, which corresponds precisely to -3.01 dB."}
        ]
    },

    # 17. Band-pass and Band-stop Filters
    {
        "category_code": "DSP",
        "title": "Band-Pass and Band-Stop (Notch) Filters",
        "slug": "bandpass-bandstop-filters",
        "objective": "To design a band-pass filter to isolate a specific band and a notch filter to eliminate 50 Hz power-line hum.",
        "theory": (
            "A band-pass filter allows signals within [f_low, f_high] to pass while attenuating frequencies outside. "
            "A notch (band-stop) filter introduces deep attenuation zeros at a specific interference frequency f0 (such as 50 Hz or 60 Hz hum) "
            "with narrow notch bandwidth defined by quality factor Q = f0 / delta_f."
        ),
        "equations_json": [
            "H_{\\text{notch}}(z) = \\frac{1 - 2\\cos(\\omega_0) z^{-1} + z^{-2}}{1 - 2r\\cos(\\omega_0) z^{-1} + r^2 z^{-2}}, \\quad r \\approx 0.95 - 0.99",
            "Q = \\frac{f_0}{\\Delta f_{3\\text{dB}}} \\text{ (Quality Factor)}"
        ],
        "procedure_json": [
            "Set sampling frequency fs = 1000 Hz",
            "Synthesize noisy ECG signal containing 50 Hz power-line interference",
            "Design second-order IIR notch filter at f0 = 50 Hz using signal.iirnotch()",
            "Filter signal and plot power spectrum before and after notch filtration"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import scipy.signal as signal\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 1000.0\n"
            "f0 = 50.0         # 50 Hz hum to eliminate\n"
            "Q = 30.0          # Quality factor (narrow notch)\n\n"
            "# 1. Design IIR notch filter\n"
            "b_notch, a_notch = signal.iirnotch(f0, Q, fs=fs)\n\n"
            "# 2. Test signal: 10 Hz desired signal + 50 Hz loud hum\n"
            "t = np.arange(0, 0.5, 1/fs)\n"
            "desired = np.sin(2 * np.pi * 10 * t)\n"
            "hum = 0.8 * np.sin(2 * np.pi * 50 * t)\n"
            "dirty = desired + hum\n\n"
            "# 3. Filter using lfilter\n"
            "cleaned = signal.lfilter(b_notch, a_notch, dirty)\n\n"
            "fig, axs = plt.subplots(2, 1, figsize=(9, 6))\n"
            "w, H = signal.freqz(b_notch, a_notch, worN=1024, fs=fs)\n"
            "axs[0].plot(w, 20 * np.log10(np.abs(H)), 'b-', lw=1.8)\n"
            "axs[0].set_title('50 Hz Notch Filter Frequency Response (Deep Null at 50 Hz)')\n"
            "axs[0].set_xlabel('Frequency (Hz)'); axs[0].set_ylabel('Gain (dB)'); axs[0].set_xlim(0, 100); axs[0].grid(True)\n\n"
            "axs[1].plot(t, dirty, 'r--', alpha=0.6, label='Corrupted Signal (10 Hz + 50 Hz Hum)')\n"
            "axs[1].plot(t, cleaned, 'g-', lw=1.8, label='Filtered Output (Hum Removed)')\n"
            "axs[1].set_title('Time Domain Notch Filtration Result')\n"
            "axs[1].set_xlabel('Time (s)'); axs[1].grid(True); axs[1].legend()\n"
            "plt.tight_layout()\n"
            "print(f'50 Hz Notch filter applied successfully with Q = {Q}.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport scipy.signal as signal\nimport matplotlib.pyplot as plt\n"
            "b, a = signal.iirnotch(50, 30, fs=1000)\n"
            "w, H = signal.freqz(b, a, fs=1000)\n"
            "plt.plot(w[:200], 20*np.log10(np.abs(H[:200]))); plt.grid(True); plt.title('50 Hz Notch')\n"
            "print('Notch filter designed.')\n"
        ),
        "matlab_code": (
            "% Notch Filter\n"
            "clear all; close all; clc;\n"
            "fs = 1000; f0 = 50; Q = 30; w0 = f0/(fs/2); bw = w0/Q;\n"
            "[b, a] = iirnotch(w0, bw);\n"
            "[H, f] = freqz(b, a, 512, fs);\n"
            "figure(1); plot(f(1:100), 20*log10(abs(H(1:100)))); grid on; title('50 Hz Notch Filter');\n"
            "disp('Notch filter verified.');\n"
        ),
        "expected_output": "50 Hz Notch filter applied successfully with Q = 30.0.",
        "viva_questions_json": [
            {"question": "Where are the zeros of a 50 Hz digital notch filter placed?", "answer": "On the unit circle at angle theta = +- 2*pi*(50/fs), giving exact zero transmission at 50 Hz."},
            {"question": "How does quality factor Q affect the notch filter?", "answer": "A higher Q yields a narrower 3 dB rejection bandwidth, preserving adjacent signal frequencies with less phase distortion."}
        ]
    },

    # 18. Amplitude Modulation
    {
        "category_code": "DSP",
        "title": "Amplitude Modulation (AM DSB-FC) & Demodulation",
        "slug": "amplitude-modulation",
        "objective": "To synthesize Double Sideband Full Carrier AM signals for varied modulation indices and perform envelope detection.",
        "theory": (
            "Standard amplitude modulation superimposes a baseband message m(t) onto high-frequency carrier c(t): "
            "s_AM(t) = A_c * [1 + mu * cos(2*pi*f_m*t)] * cos(2*pi*f_c*t). "
            "When mu <= 1, the envelope faithfully matches m(t) without crossing zero, allowing simple diode envelope detection."
        ),
        "equations_json": [
            "s_{\\text{AM}}(t) = A_c [1 + \\mu m(t)] \\cos(2\\pi f_c t)",
            "\\mu = \\frac{A_m}{A_c} \\text{ (Modulation Index)}",
            "P_{\\text{total}} = P_c \\left(1 + \\frac{\\mu^2}{2}\\right)"
        ],
        "procedure_json": [
            "Set carrier frequency fc = 200 Hz and message frequency fm = 15 Hz at fs = 4000 Hz",
            "Generate under-modulated (mu = 0.5) and over-modulated (mu = 1.4) signals",
            "Simulate simple diode envelope detector (rectifier + lowpass)",
            "Plot modulated waveforms and recovered message signal"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import scipy.signal as signal\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 4000.0\n"
            "t = np.arange(0, 0.15, 1/fs)\n"
            "Ac = 4.0; fc = 200.0\n"
            "Am = 2.0; fm = 15.0\n\n"
            "m = np.cos(2 * np.pi * fm * t)\n"
            "carrier = np.cos(2 * np.pi * fc * t)\n\n"
            "mu = Am / Ac   # mu = 0.5\n"
            "s_am = Ac * (1 + mu * m) * carrier\n\n"
            "# Envelope detection: Half-wave rectification + lowpass filter\n"
            "rectified = np.maximum(0, s_am)\n"
            "b, a = signal.butter(4, 2 * fm, btype='low', fs=fs)\n"
            "recovered = signal.filtfilt(b, a, rectified) - Ac/np.pi\n\n"
            "plt.figure(figsize=(9, 6))\n"
            "plt.subplot(2, 1, 1)\n"
            "plt.plot(t, s_am, 'b-', label='Modulated AM Wave (\\mu = 0.5)')\n"
            "plt.plot(t, Ac * (1 + mu * m), 'r--', label='Upper Envelope')\n"
            "plt.title('Standard Amplitude Modulation (AM DSB-FC)')\n"
            "plt.grid(True); plt.legend()\n\n"
            "plt.subplot(2, 1, 2)\n"
            "plt.plot(t, m, 'k--', label='Original Message m(t)')\n"
            "plt.plot(t, recovered / np.max(recovered), 'g-', lw=1.8, label='Demodulated Envelope')\n"
            "plt.title('Demodulated Baseband Message Signal')\n"
            "plt.xlabel('Time (s)'); plt.grid(True); plt.legend()\n"
            "plt.tight_layout()\n"
            "print(f'Modulation index: \\mu = {mu:.2f} | Envelope detection successful.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "t = np.linspace(0, 0.1, 1000); m = np.cos(2*np.pi*20*t); c = np.cos(2*np.pi*200*t)\n"
            "s_am = (1 + 0.6 * m) * c\n"
            "plt.plot(t, s_am); plt.title('AM Wave'); plt.grid(True)\n"
            "print('AM generation completed.')\n"
        ),
        "matlab_code": (
            "% Amplitude Modulation\n"
            "clear all; close all; clc;\n"
            "t = 0:0.0001:0.1; m = cos(2*pi*20*t); c = cos(2*pi*200*t);\n"
            "s_am = (1 + 0.6 * m) .* c;\n"
            "figure(1); plot(t, s_am); grid on; title('AM Signal');\n"
            "disp('AM generation completed.');\n"
        ),
        "expected_output": "Envelope detection successful.",
        "viva_questions_json": [
            {"question": "What is the bandwidth of a standard AM DSB-FC signal?", "answer": "The bandwidth is exactly twice the maximum baseband message frequency: BW = 2 * fm."},
            {"question": "What power efficiency does standard AM achieve at maximum modulation mu = 1?", "answer": "At mu = 1, sideband power is 1/3 (33.3%) of total transmitted power; the carrier consumes 66.7% of power without carrying information."}
        ]
    },

    # 19. Frequency Modulation
    {
        "category_code": "DSP",
        "title": "Frequency Modulation (FM) & Spectrum",
        "slug": "frequency-modulation",
        "objective": "To synthesize an angle-modulated Frequency Modulated (FM) signal and verify Carson's bandwidth rule.",
        "theory": (
            "In Frequency Modulation, the instantaneous carrier frequency varies linearly with the message signal: "
            "f_i(t) = f_c + k_f * m(t). The modulated signal is s_FM(t) = A_c * cos(2*pi*f_c*t + beta * sin(2*pi*f_m*t)), "
            "where beta = delta_f / f_m is the modulation index. Transmission bandwidth is given by Carson's rule: B_T = 2*(delta_f + f_m)."
        ),
        "equations_json": [
            "s_{\\text{FM}}(t) = A_c \\cos\\left( 2\\pi f_c t + \\beta \\sin(2\\pi f_m t) \\right)",
            "\\beta = \\frac{\\Delta f}{f_m} \\text{ (Modulation Index)}",
            "B_T \\approx 2(\\Delta f + f_m) = 2 f_m (\\beta + 1) \\text{ (Carson's Rule)}"
        ],
        "procedure_json": [
            "Set carrier fc = 250 Hz, message fm = 15 Hz, and frequency deviation delta_f = 60 Hz (beta = 4)",
            "Synthesize FM waveform showing compression during message peaks and dilation during troughs",
            "Compute FFT spectrum showing multiple Bessel sidebands symmetric around fc",
            "Verify effective bandwidth matches Carson's prediction"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 4000.0\n"
            "t = np.arange(0, 0.2, 1/fs)\n"
            "Ac = 2.0; fc = 250.0\n"
            "fm = 15.0; delta_f = 60.0\n"
            "beta = delta_f / fm  # beta = 4.0\n\n"
            "m = np.cos(2 * np.pi * fm * t)\n"
            "s_fm = Ac * np.cos(2 * np.pi * fc * t + beta * np.sin(2 * np.pi * fm * t))\n\n"
            "# Carson's bandwidth\n"
            "BW_carson = 2 * (delta_f + fm)\n\n"
            "fig, axs = plt.subplots(2, 1, figsize=(9, 6))\n"
            "axs[0].plot(t, s_fm, 'b-', lw=1.2)\n"
            "axs[0].set_title(f'FM Time Waveform (\\beta = {beta}, \\Delta f = {delta_f} Hz)')\n"
            "axs[0].set_xlabel('Time (s)'); axs[0].grid(True)\n\n"
            "N = 2048\n"
            "S_fft = np.abs(np.fft.fft(s_fm, N))\n"
            "freqs = np.fft.fftfreq(N, 1/fs)\n"
            "axs[1].plot(freqs[:N//2], S_fft[:N//2], 'r-', lw=1.5)\n"
            "axs[1].set_title(f'FM Bessel Sideband Spectrum (Carson BW = {BW_carson:.1f} Hz)')\n"
            "axs[1].set_xlabel('Frequency (Hz)'); axs[1].set_xlim(fc - 120, fc + 120); axs[1].grid(True)\n"
            "plt.tight_layout()\n"
            "print(f'Modulation index \\beta: {beta:.2f}')\n"
            "print(f'Carson Transmission Bandwidth: {BW_carson:.1f} Hz')\n"
        ),
        "python_code": (
            "import numpy as np\nimport matplotlib.pyplot as plt\n"
            "t = np.linspace(0, 0.1, 1000); fm = 10; fc = 100; beta = 5\n"
            "s_fm = np.cos(2*np.pi*fc*t + beta*np.sin(2*np.pi*fm*t))\n"
            "plt.plot(t, s_fm); plt.title('FM Wave'); plt.grid(True)\n"
            "print('FM generated successfully.')\n"
        ),
        "matlab_code": (
            "% Frequency Modulation\n"
            "clear all; close all; clc;\n"
            "t = 0:0.0001:0.1; fm = 10; fc = 100; beta = 5;\n"
            "s_fm = cos(2*pi*fc*t + beta*sin(2*pi*fm*t));\n"
            "figure(1); plot(t, s_fm); grid on; title('FM Waveform');\n"
            "disp('FM generated successfully.');\n"
        ),
        "expected_output": "Carson Transmission Bandwidth:",
        "viva_questions_json": [
            {"question": "Why is the theoretical bandwidth of an FM signal infinite?", "answer": "The Bessel function expansion of frequency modulation yields an infinite number of sidebands J_n(beta) * cos(2*pi*(fc + n*fm)*t) for all integer n."},
            {"question": "Why does FM offer superior noise immunity compared to AM?", "answer": "Amplitude noise affects the envelope of the signal, which an FM receiver's amplitude limiter clips off without corrupting the zero-crossing frequency information."}
        ]
    },

    # 20. Power Spectral Density
    {
        "category_code": "DSP",
        "title": "Power Spectral Density (PSD) Estimation",
        "slug": "power-spectral-density",
        "objective": "To estimate the Power Spectral Density distribution of a signal obscured by white noise using Welch's averaged periodogram method.",
        "theory": (
            "The Power Spectral Density (PSD) describes how signal power is distributed across frequencies. "
            "While a raw periodogram exhibits high variance that does not decrease as sample length increases, "
            "Welch's method divides data into overlapping windowed segments and averages their modified periodograms, "
            "dramatically reducing spectral variance."
        ),
        "equations_json": [
            "P_{xx}(f) = \\lim_{T \\to \\infty} \\frac{1}{T} E\\left\\{ |X_T(f)|^2 \\right\\}",
            "\\hat{P}_{\\text{Welch}}(f) = \\frac{1}{K} \\sum_{i=1}^{K} I_i(f) \\text{ (Averaged Modified Periodogram)}"
        ],
        "procedure_json": [
            "Create a test signal with two sinusoids at 40 Hz and 110 Hz buried in Gaussian noise",
            "Compute raw FFT periodogram",
            "Compute Welch's averaged periodogram using signal.welch() with Hanning window and 50% overlap",
            "Compare noisy raw periodogram with smooth Welch spectral estimate"
        ],
        "engine": "python",
        "default_code": (
            "import numpy as np\n"
            "import scipy.signal as signal\n"
            "import matplotlib.pyplot as plt\n\n"
            "fs = 1000.0\n"
            "N = 2000\n"
            "t = np.arange(N) / fs\n\n"
            "np.random.seed(42)\n"
            "# 40 Hz and 110 Hz signals buried in white noise\n"
            "sig = np.sin(2 * np.pi * 40 * t) + 1.2 * np.sin(2 * np.pi * 110 * t)\n"
            "noise = 2.0 * np.random.randn(N)\n"
            "x = sig + noise\n\n"
            "# 1. Welch PSD Estimation\n"
            "f_welch, psd_welch = signal.welch(x, fs=fs, window='hann', nperseg=256, noverlap=128)\n\n"
            "# 2. Raw Periodogram for comparison\n"
            "f_raw, psd_raw = signal.periodogram(x, fs=fs)\n\n"
            "plt.figure(figsize=(9, 5))\n"
            "plt.semilogy(f_raw, psd_raw, 'gray', alpha=0.5, label='Raw Periodogram (High Variance)')\n"
            "plt.semilogy(f_welch, psd_welch, 'b-', lw=2, label=\"Welch's Method (Smooth Estimate)\")\n"
            "plt.axvline(40, color='r', linestyle='--', label='Tone 1: 40 Hz')\n"
            "plt.axvline(110, color='g', linestyle='--', label='Tone 2: 110 Hz')\n"
            "plt.title('Power Spectral Density (PSD) Estimation via Welch\\'s Method')\n"
            "plt.xlabel('Frequency (Hz)'); plt.ylabel('Power Density (V²/Hz)')\n"
            "plt.xlim(0, 250); plt.grid(True, which='both')\n"
            "plt.legend()\n"
            "plt.tight_layout()\n"
            "print('PSD estimation completed: Clear peaks identified at 40 Hz and 110 Hz.')\n"
        ),
        "python_code": (
            "import numpy as np\nimport scipy.signal as signal\nimport matplotlib.pyplot as plt\n"
            "fs = 1000; t = np.arange(1000)/fs; x = np.sin(2*np.pi*40*t) + np.random.randn(1000)\n"
            "f, psd = signal.welch(x, fs=fs, nperseg=128)\n"
            "plt.semilogy(f, psd); plt.grid(True); plt.title('Welch PSD')\n"
            "print('PSD computed.')\n"
        ),
        "matlab_code": (
            "% Power Spectral Density\n"
            "clear all; close all; clc;\n"
            "fs = 1000; t = (0:999)/fs; x = sin(2*pi*40*t) + randn(size(t));\n"
            "[psd, f] = pwelch(x, 128, 64, 128, fs);\n"
            "figure(1); semilogy(f, psd); grid on; title('Welch PSD');\n"
            "disp('PSD computed.');\n"
        ),
        "expected_output": "PSD estimation completed: Clear peaks identified at 40 Hz and 110 Hz.",
        "viva_questions_json": [
            {"question": "Why is the raw periodogram considered an inconsistent statistical estimator?", "answer": "The variance of the raw periodogram does not approach zero as the observation length N tends to infinity; it stays constant proportional to the true spectrum squared."},
            {"question": "What is the trade-off in choosing the segment length in Welch's method?", "answer": "Shorter segment lengths yield more segments to average (reducing variance) but degrade frequency resolution (broadening spectral peaks)."}
        ]
    }
]
