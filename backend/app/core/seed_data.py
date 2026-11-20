EXPERIMENT_CATEGORIES = [
    {
        "name": "Digital Signal Processing",
        "code": "DSP",
        "description": "Fundamental digital signal generation, convolution, discrete transforms, and digital filter design.",
        "display_order": 1
    },
    {
        "name": "Communication Systems",
        "code": "COMM",
        "description": "Analog and digital modulation techniques, carrier keying, constellation analysis, and BER performance.",
        "display_order": 2
    },
    {
        "name": "Control Systems",
        "code": "CONTROL",
        "description": "Linear time-invariant systems, transient response, PID controllers, and stability margins.",
        "display_order": 3
    }
]

EXPERIMENTS = [
    # 1. DSP: Sine Wave Generation
    {
        "category_code": "DSP",
        "title": "Continuous & Discrete Sine Wave Generation",
        "slug": "sine-wave-generation",
        "objective": "To synthesize and visualize continuous-time and discrete-time sinusoidal signals of specified frequency and amplitude.",
        "theory": "A sinusoidal signal is mathematically represented as $x(t) = A \\sin(2\\pi f t + \\phi)$. In discrete-time, sampling at rate $f_s$ yields $x[n] = A \\sin(2\\pi (f/f_s) n + \\phi)$.",
        "equations_json": ["x(t) = A \\sin(2\\pi f t + \\phi)", "x[n] = A \\sin(\\omega_0 n + \\phi)"],
        "procedure_json": ["Define amplitude A, frequency f, and sampling frequency fs", "Compute time vector t = 0:1/fs:duration", "Evaluate signal x = A*sin(2*pi*f*t)", "Plot continuous curve and discrete stem sequence"],
        "engine": "octave",
        "default_code": (
            "% Experiment 1: Sine Wave Generation\n"
            "clear all; close all; clc;\n\n"
            "A = 2.5;            % Amplitude (Volts)\n"
            "f = 10;             % Signal Frequency (Hz)\n"
            "fs = 200;           % Sampling Frequency (Hz)\n"
            "t = 0:1/fs:0.5;     % Time vector for 0.5s\n\n"
            "x = A * sin(2 * pi * f * t);\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "plot(t, x, 'b-', 'LineWidth', 1.5);\n"
            "grid on;\n"
            "title('Continuous-time Representation x(t)');\n"
            "xlabel('Time (s)'); ylabel('Amplitude (V)');\n\n"
            "subplot(2, 1, 2);\n"
            "stem(t(1:30), x(1:30), 'r', 'filled');\n"
            "grid on;\n"
            "title('Discrete Samples x[n] (First 30 samples)');\n"
            "xlabel('Time (s)'); ylabel('Amplitude (V)');\n"
            "disp('Sine wave generated successfully.');\n"
        ),
        "expected_output": "Sine wave generated successfully."
    },
    # 2. DSP: Unit Impulse and Step Response
    {
        "category_code": "DSP",
        "title": "Unit Impulse and Unit Step Sequences",
        "slug": "unit-impulse-step",
        "objective": "To generate standard elementary discrete-time signals: unit impulse delta[n] and unit step u[n].",
        "theory": "The unit impulse is defined as $\\delta[n] = 1$ for $n=0$ and $0$ otherwise. The unit step is $u[n] = 1$ for $n \\ge 0$ and $0$ for $n < 0$.",
        "equations_json": ["\\delta[n] = \\begin{cases} 1, & n = 0 \\\\ 0, & n \\neq 0 \\end{cases}", "u[n] = \\sum_{k=0}^{\\infty} \\delta[n-k]"],
        "procedure_json": ["Define sample index vector n = -10:10", "Generate impulse delta = (n == 0)", "Generate step u = (n >= 0)", "Plot using stem() function"],
        "engine": "octave",
        "default_code": (
            "% Experiment 2: Unit Impulse & Step Response\n"
            "clear all; close all; clc;\n\n"
            "n = -10:1:10;\n"
            "delta = (n == 0);\n"
            "u = (n >= 0);\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "stem(n, delta, 'b', 'filled', 'LineWidth', 1.5);\n"
            "grid on;\n"
            "title('Unit Impulse Sequence \\delta[n]');\n"
            "xlabel('Sample Index n'); ylabel('Amplitude');\n\n"
            "subplot(2, 1, 2);\n"
            "stem(n, u, 'm', 'filled', 'LineWidth', 1.5);\n"
            "grid on;\n"
            "title('Unit Step Sequence u[n]');\n"
            "xlabel('Sample Index n'); ylabel('Amplitude');\n"
            "disp('Impulse and step sequences plotted.');\n"
        ),
        "expected_output": "Impulse and step sequences plotted."
    },
    # 3. DSP: Nyquist Sampling Theorem
    {
        "category_code": "DSP",
        "title": "Verification of Nyquist Sampling Theorem",
        "slug": "sampling-theorem",
        "objective": "To observe the effects of under-sampling (aliasing), critical sampling, and over-sampling on a continuous signal.",
        "theory": "The Nyquist-Shannon sampling theorem states that a continuous-time bandlimited signal with maximum frequency $f_m$ can be reconstructed if the sampling frequency $f_s \\ge 2 f_m$. When $f_s < 2f_m$, high frequencies fold into lower frequencies (aliasing).",
        "equations_json": ["f_s \\ge 2 f_{max}", "f_{apparent} = |f - k f_s|"],
        "procedure_json": ["Generate reference analog signal at high sampling rate", "Sample at fs < 2fm (under-sampling)", "Sample at fs >= 2fm (proper sampling)", "Compare reconstructed waveforms"],
        "engine": "octave",
        "default_code": (
            "% Experiment 3: Nyquist Sampling Theorem\n"
            "clear all; close all; clc;\n\n"
            "fm = 20;              % Signal maximum frequency 20 Hz\n"
            "t_analog = 0:0.0001:0.2;\n"
            "x_analog = sin(2*pi*fm*t_analog);\n\n"
            "% Case 1: Under-sampled (fs1 < 2*fm)\n"
            "fs1 = 25; t1 = 0:1/fs1:0.2; x1 = sin(2*pi*fm*t1);\n\n"
            "% Case 2: Nyquist rate (fs2 = 2*fm)\n"
            "fs2 = 40; t2 = 0:1/fs2:0.2; x2 = sin(2*pi*fm*t2);\n\n"
            "% Case 3: Over-sampled (fs3 >> 2*fm)\n"
            "fs3 = 200; t3 = 0:1/fs3:0.2; x3 = sin(2*pi*fm*t3);\n\n"
            "figure(1);\n"
            "subplot(3, 1, 1);\n"
            "plot(t_analog, x_analog, 'k--', t1, x1, 'r-o'); grid on;\n"
            "title('Under-sampled: fs = 25 Hz < 2*fm (Aliasing)');\n\n"
            "subplot(3, 1, 2);\n"
            "plot(t_analog, x_analog, 'k--', t2, x2, 'b-o'); grid on;\n"
            "title('Critical Sampling: fs = 40 Hz = 2*fm');\n\n"
            "subplot(3, 1, 3);\n"
            "plot(t_analog, x_analog, 'k--', t3, x3, 'g-o'); grid on;\n"
            "title('Over-sampled: fs = 200 Hz >> 2*fm (Faithful)');\n"
            "disp('Sampling theorem verified.');\n"
        ),
        "expected_output": "Sampling theorem verified."
    },
    # 4. DSP: Linear Convolution
    {
        "category_code": "DSP",
        "title": "Linear Convolution of Two Discrete Sequences",
        "slug": "linear-convolution",
        "objective": "To compute and plot the linear convolution of input sequence x[n] with impulse response h[n].",
        "theory": "Linear convolution calculates the output of an LTI system: $y[n] = x[n] * h[n] = \\sum_{k=-\\infty}^{\\infty} x[k] h[n-k]$. If $x$ has length $L_1$ and $h$ has length $L_2$, $y$ has length $L_1 + L_2 - 1$.",
        "equations_json": ["y[n] = \\sum_{k=0}^{L_1-1} x[k] h[n-k]", "Length(y) = L_x + L_h - 1"],
        "procedure_json": ["Define input x[n] and system response h[n]", "Compute convolution using conv()", "Plot x[n], h[n], and y[n]"],
        "engine": "octave",
        "default_code": (
            "% Experiment 4: Linear Convolution\n"
            "clear all; close all; clc;\n\n"
            "x = [1, 2, 3, 1];       % Input sequence\n"
            "h = [1, 1, 1];          % Impulse response\n"
            "y = conv(x, h);         % Linear convolution\n\n"
            "disp('Input sequence x:'); disp(x);\n"
            "disp('Impulse response h:'); disp(h);\n"
            "disp('Convolution result y:'); disp(y);\n\n"
            "figure(1);\n"
            "subplot(3, 1, 1); stem(0:length(x)-1, x, 'b', 'filled'); grid on; title('Input x[n]');\n"
            "subplot(3, 1, 2); stem(0:length(h)-1, h, 'm', 'filled'); grid on; title('Impulse Response h[n]');\n"
            "subplot(3, 1, 3); stem(0:length(y)-1, y, 'r', 'filled'); grid on; title('Convolved Output y[n] = x[n]*h[n]');\n"
        ),
        "expected_output": "Convolution result y: [ 1 3 6 6 4 1 ]"
    },
    # 5. DSP: Low-Pass FIR Filter Design
    {
        "category_code": "DSP",
        "title": "FIR Low-Pass Filter Design via Windowing",
        "slug": "fir-filter-design",
        "objective": "To design a linear phase FIR Low-Pass filter using the Hamming window technique.",
        "theory": "The ideal low-pass impulse response $h_d[n] = \\frac{\\sin(\\omega_c (n-M))}{\\pi (n-M)}$. Multiplying with window $w[n]$ yields causal FIR filter coefficients $h[n] = h_d[n] w[n]$.",
        "equations_json": ["h_d[n] = \\frac{\\sin(\\omega_c (n-\\tau))}{\\pi (n-\\tau)}", "w_{hamming}[n] = 0.54 - 0.46 \\cos(2\\pi n / M)"],
        "procedure_json": ["Set filter order N and cutoff frequency wc", "Compute Hamming window coefficients", "Calculate impulse response", "Plot frequency magnitude and phase response"],
        "engine": "octave",
        "default_code": (
            "% Experiment 5: FIR Low-Pass Filter Design\n"
            "clear all; close all; clc;\n\n"
            "N = 31;                 % Filter order (odd number of taps)\n"
            "fc = 1200;              % Cutoff frequency (Hz)\n"
            "fs = 8000;              % Sampling frequency (Hz)\n"
            "wc = 2 * pi * fc / fs;  % Normalized digital cutoff\n\n"
            "M = (N - 1) / 2;\n"
            "n = 0:N-1;\n"
            "m = n - M + eps;        % Avoid divide-by-zero at center\n"
            "hd = sin(wc * m) ./ (pi * m);\n"
            "w = 0.54 - 0.46 * cos(2 * pi * n / (N - 1)); % Hamming window\n"
            "h = hd .* w;            % Designed filter taps\n\n"
            "% Frequency response\n"
            "[H, f] = freqz(h, 1, 512, fs);\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "plot(f, 20*log10(abs(H)), 'b-', 'LineWidth', 1.5);\n"
            "grid on;\n"
            "title('FIR Low-Pass Filter Magnitude Response');\n"
            "xlabel('Frequency (Hz)'); ylabel('Magnitude (dB)');\n\n"
            "subplot(2, 1, 2);\n"
            "plot(f, angle(H)*180/pi, 'r-', 'LineWidth', 1.2);\n"
            "grid on;\n"
            "title('Linear Phase Response');\n"
            "xlabel('Frequency (Hz)'); ylabel('Phase (degrees)');\n"
            "disp('FIR filter designed successfully.');\n"
        ),
        "expected_output": "FIR filter designed successfully."
    },
    # 6. COMM: Amplitude Modulation (AM DSB-FC)
    {
        "category_code": "COMM",
        "title": "Amplitude Modulation (AM DSB-FC) & Demodulation",
        "slug": "amplitude-modulation",
        "objective": "To generate an amplitude modulated waveform for different modulation indices (under, critical, and over-modulation).",
        "theory": "The standard AM equation is $s(t) = [A_c + m(t)] \\cos(2\\pi f_c t) = A_c [1 + \\mu \\cos(2\\pi f_m t)] \\cos(2\\pi f_c t)$, where $\\mu = A_m / A_c$ is the modulation index.",
        "equations_json": ["s(t) = A_c [1 + \\mu \\cos(2\\pi f_m t)] \\cos(2\\pi f_c t)", "\\mu = \\frac{A_m}{A_c}"],
        "procedure_json": ["Generate message signal m(t) with frequency fm", "Generate carrier signal c(t) with fc >> fm", "Modulate with mu = 0.5 (under-modulation) and mu = 1.0 (critical)", "Observe envelope patterns"],
        "engine": "octave",
        "default_code": (
            "% Experiment 6: Amplitude Modulation (AM DSB-FC)\n"
            "clear all; close all; clc;\n\n"
            "Ac = 5;                 % Carrier amplitude\n"
            "fc = 100;               % Carrier frequency (Hz)\n"
            "fm = 10;                % Modulating signal frequency (Hz)\n"
            "fs = 2000;              % Sampling rate\n"
            "t = 0:1/fs:0.1;         % Time duration 100ms\n\n"
            "m = cos(2 * pi * fm * t); % Baseband message\n"
            "c = cos(2 * pi * fc * t); % High-frequency carrier\n\n"
            "% Case 1: Under-modulation (mu = 0.5)\n"
            "mu1 = 0.5;\n"
            "s1 = Ac * (1 + mu1 * m) .* c;\n\n"
            "% Case 2: Over-modulation (mu = 1.4)\n"
            "mu2 = 1.4;\n"
            "s2 = Ac * (1 + mu2 * m) .* c;\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "plot(t, s1, 'b-', 'LineWidth', 1.2);\n"
            "grid on;\n"
            "title('Under-Modulated AM Signal (\\mu = 0.5 - Clean Envelope)');\n"
            "xlabel('Time (s)'); ylabel('Amplitude (V)');\n\n"
            "subplot(2, 1, 2);\n"
            "plot(t, s2, 'r-', 'LineWidth', 1.2);\n"
            "grid on;\n"
            "title('Over-Modulated AM Signal (\\mu = 1.4 - Phase Inversion / Distortion)');\n"
            "xlabel('Time (s)'); ylabel('Amplitude (V)');\n"
            "disp('AM modulation simulation complete.');\n"
        ),
        "expected_output": "AM modulation simulation complete."
    },
    # 7. COMM: Binary Phase Shift Keying (BPSK)
    {
        "category_code": "COMM",
        "title": "Binary Phase Shift Keying (BPSK) Modulation",
        "slug": "bpsk-modulation",
        "objective": "To modulate and demodulate a digital bit stream using BPSK and plot the time-domain waveform and constellation points.",
        "theory": "In BPSK, binary '1' is transmitted as $s_1(t) = A \\cos(2\\pi f_c t)$ and binary '0' as $s_0(t) = -A \\cos(2\\pi f_c t) = A \\cos(2\\pi f_c t + \\pi)$, corresponding to a $180^\\circ$ phase flip.",
        "equations_json": ["s(t) = \\sqrt{\\frac{2E_b}{T_b}} d(t) \\cos(2\\pi f_c t)", "d(t) \\in \\{+1, -1\\}"],
        "procedure_json": ["Generate random binary bitstream [1, 0, 1, 1, 0]", "Map to NRZ polar format [+1, -1]", "Multiply with high-frequency sinusoidal carrier", "Observe phase reversals at bit transitions"],
        "engine": "octave",
        "default_code": (
            "% Experiment 7: BPSK Modulation\n"
            "clear all; close all; clc;\n\n"
            "bits = [1, 0, 1, 1, 0, 1, 0, 0];\n"
            "N = length(bits);\n"
            "Tb = 0.01;              % Bit duration 10 ms\n"
            "fc = 200;               % Carrier frequency 200 Hz\n"
            "fs = 4000;              % Sampling rate\n"
            "samples_per_bit = fs * Tb;\n\n"
            "t = 0:1/fs:(N*Tb - 1/fs);\n"
            "carrier = cos(2 * pi * fc * t);\n\n"
            "% Polar NRZ signal\n"
            "nrz = [];\n"
            "for b = bits\n"
            "    val = (b == 1) * 2 - 1; % Maps 1 -> +1, 0 -> -1\n"
            "    nrz = [nrz, val * ones(1, samples_per_bit)];\n"
            "end\n\n"
            "bpsk_sig = nrz .* carrier;\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "plot(t, nrz, 'LineWidth', 2); axis([0 t(end) -1.5 1.5]); grid on;\n"
            "title('Digital Baseband Bitstream (NRZ)');\n"
            "xlabel('Time (s)'); ylabel('Logic Level');\n\n"
            "subplot(2, 1, 2);\n"
            "plot(t, bpsk_sig, 'r', 'LineWidth', 1.2); grid on;\n"
            "title('BPSK Modulated Carrier (Phase Flips at Transitions)');\n"
            "xlabel('Time (s)'); ylabel('Carrier Amplitude');\n"
            "disp('BPSK modulation completed.');\n"
        ),
        "expected_output": "BPSK modulation completed."
    },
    # 8. CONTROL: Step Response of Second-Order System
    {
        "category_code": "CONTROL",
        "title": "Second-Order System Transient Analysis",
        "slug": "second-order-step-response",
        "objective": "To determine transient specifications (Rise time, Peak time, Max overshoot, Settling time) for varied damping ratios (zeta).",
        "theory": "The standard closed-loop second-order transfer function is $T(s) = \\frac{\\omega_n^2}{s^2 + 2\\zeta \\omega_n s + \\omega_n^2}$. The damping ratio $\\zeta$ dictates system dynamics: $\\zeta < 1$ (underdamped), $\\zeta = 1$ (critically damped), $\\zeta > 1$ (overdamped).",
        "equations_json": ["T(s) = \\frac{\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}", "M_p = e^{-\\pi\\zeta / \\sqrt{1-\\zeta^2}} \\times 100\\%"],
        "procedure_json": ["Set natural frequency wn = 5 rad/s", "Define damping ratios: zeta = [0.2, 0.5, 0.707, 1.0]", "Compute analytic step response", "Overlay responses to observe overshoot vs damping"],
        "engine": "octave",
        "default_code": (
            "% Experiment 8: Second-Order Step Response Analysis\n"
            "clear all; close all; clc;\n\n"
            "wn = 5;                  % Natural frequency = 5 rad/s\n"
            "t = 0:0.01:3;            % Time span 3 seconds\n"
            "zetas = [0.2, 0.5, 0.707, 1.0];\n"
            "colors = {'r', 'b', 'g', 'k'};\n\n"
            "figure(1);\n"
            "hold on;\n"
            "for i = 1:length(zetas)\n"
            "    z = zetas(i);\n"
            "    if z < 1\n"
            "        wd = wn * sqrt(1 - z^2);\n"
            "        phi = atan(sqrt(1 - z^2) / z);\n"
            "        y = 1 - (exp(-z * wn * t) / sqrt(1 - z^2)) .* sin(wd * t + phi);\n"
            "    else\n"
            "        y = 1 - exp(-wn * t) .* (1 + wn * t);\n"
            "    end\n"
            "    plot(t, y, colors{i}, 'LineWidth', 1.8);\n"
            "end\n"
            "hold off;\n"
            "grid on;\n"
            "title('Second-Order System Step Response for Varied Damping Ratio \\zeta');\n"
            "xlabel('Time (seconds)'); ylabel('Output Amplitude c(t)');\n"
            "legend('\\zeta = 0.2 (High overshoot)', '\\zeta = 0.5', '\\zeta = 0.707 (Optimal)', '\\zeta = 1.0 (Critically damped)');\n"
            "disp('Second order transient analysis plotted.');\n"
        ),
        "expected_output": "Second order transient analysis plotted."
    },
    # 9. CONTROL: PID Controller Tuning
    {
        "category_code": "CONTROL",
        "title": "Closed-Loop PID Controller Simulation",
        "slug": "pid-controller-tuning",
        "objective": "To implement proportional, integral, and derivative control and evaluate steady-state error reduction.",
        "theory": "The PID control law is $u(t) = K_p e(t) + K_i \\int_0^t e(\\tau)d\\tau + K_d \\frac{de(t)}{dt}$. $K_p$ improves rise time, $K_i$ eliminates steady-state offset, and $K_d$ dampens oscillatory overshoot.",
        "equations_json": ["u(t) = K_p e(t) + K_i \\int e dt + K_d \\frac{de}{dt}", "E(s) = R(s) - Y(s)"],
        "procedure_json": ["Model first-order plus dead time or mass-spring-damper plant", "Simulate open-loop uncompensated plant", "Apply P-only controller and observe offset", "Apply full PID controller and verify zero steady-state error"],
        "engine": "octave",
        "default_code": (
            "% Experiment 9: PID Controller Discrete Simulation\n"
            "clear all; close all; clc;\n\n"
            "dt = 0.01; T_sim = 5; N = T_sim / dt;\n"
            "t = 0:dt:T_sim;\n"
            "setpoint = 1.0;          % Desired target value\n\n"
            "% Plant: dy/dt + 2y = u (First order lag)\n"
            "Kp = 15; Ki = 25; Kd = 1.2;\n\n"
            "y = zeros(1, length(t));\n"
            "e_integral = 0; e_prev = 0;\n\n"
            "for k = 1:N\n"
            "    e = setpoint - y(k);\n"
            "    e_integral = e_integral + e * dt;\n"
            "    e_derivative = (e - e_prev) / dt;\n"
            "    u = Kp * e + Ki * e_integral + Kd * e_derivative;\n"
            "    % Euler update for plant dy/dt = -2*y + u\n"
            "    y(k+1) = y(k) + dt * (-2 * y(k) + u * 0.5);\n"
            "    e_prev = e;\n"
            "end\n\n"
            "figure(1);\n"
            "plot(t, y, 'b-', 'LineWidth', 2); hold on;\n"
            "plot(t, setpoint*ones(size(t)), 'r--', 'LineWidth', 1.5);\n"
            "grid on;\n"
            "title('Closed-Loop Step Response with PID Controller');\n"
            "xlabel('Time (s)'); ylabel('Process Output y(t)');\n"
            "legend('PID Response', 'Setpoint Target');\n"
            "disp('PID simulation completed successfully.');\n"
        ),
        "expected_output": "PID simulation completed successfully."
    }
]
