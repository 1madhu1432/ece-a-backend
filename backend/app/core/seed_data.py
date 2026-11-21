from app.core.dsp_experiments import DSP_EXPERIMENTS

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

OTHER_EXPERIMENTS = [
    # COMM: Binary Phase Shift Keying (BPSK)
    {
        "category_code": "COMM",
        "title": "Binary Phase Shift Keying (BPSK) Modulation",
        "slug": "bpsk-modulation",
        "objective": "To modulate and demodulate a digital bit stream using BPSK and plot the time-domain waveform and constellation points.",
        "theory": "In BPSK, binary '1' is transmitted as $s_1(t) = A \\cos(2\\pi f_c t)$ and binary '0' as $s_0(t) = -A \\cos(2\\pi f_c t)$, corresponding to a $180^\\circ$ phase flip.",
        "equations_json": ["s(t) = \\sqrt{\\frac{2E_b}{T_b}} d(t) \\cos(2\\pi f_c t)", "d(t) \\in \\{+1, -1\\}"],
        "procedure_json": ["Generate binary bitstream", "Map to NRZ polar format [+1, -1]", "Multiply with high-frequency sinusoidal carrier", "Observe phase reversals at bit transitions"],
        "engine": "octave",
        "default_code": (
            "% BPSK Modulation and Demodulation\n"
            "clear all; close all; clc;\n\n"
            "bits = [1 0 1 1 0 1 0 0];\n"
            "Tb = 0.01; fc = 200.0; fs = 4000.0;\n"
            "s_per_bit = round(fs * Tb);\n"
            "nrz = [];\n"
            "for b = bits\n"
            "    if b == 1\n"
            "        nrz = [nrz ones(1, s_per_bit)];\n"
            "    else\n"
            "        nrz = [nrz -ones(1, s_per_bit)];\n"
            "    end\n"
            "end\n"
            "t = (0:length(nrz)-1) / fs;\n"
            "carrier = cos(2 * pi * fc * t);\n"
            "bpsk = nrz .* carrier;\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "plot(t, nrz, 'b-', 'LineWidth', 2);\n"
            "grid on; title('Digital Baseband (NRZ)'); xlabel('Time (s)'); ylabel('Amplitude');\n\n"
            "subplot(2, 1, 2);\n"
            "plot(t, bpsk, 'r-', 'LineWidth', 1.2);\n"
            "grid on; title('BPSK Modulated Waveform'); xlabel('Time (s)'); ylabel('Amplitude');\n\n"
            "disp('BPSK modulation completed.');\n"
        ),
        "matlab_code": (
            "% BPSK Modulation and Demodulation\n"
            "clear all; close all; clc;\n\n"
            "bits = [1 0 1 1 0 1 0 0];\n"
            "Tb = 0.01; fc = 200.0; fs = 4000.0;\n"
            "s_per_bit = round(fs * Tb);\n"
            "nrz = [];\n"
            "for b = bits\n"
            "    if b == 1\n"
            "        nrz = [nrz ones(1, s_per_bit)];\n"
            "    else\n"
            "        nrz = [nrz -ones(1, s_per_bit)];\n"
            "    end\n"
            "end\n"
            "t = (0:length(nrz)-1) / fs;\n"
            "carrier = cos(2 * pi * fc * t);\n"
            "bpsk = nrz .* carrier;\n\n"
            "figure(1);\n"
            "subplot(2, 1, 1);\n"
            "plot(t, nrz, 'b-', 'LineWidth', 2);\n"
            "grid on; title('Digital Baseband (NRZ)'); xlabel('Time (s)'); ylabel('Amplitude');\n\n"
            "subplot(2, 1, 2);\n"
            "plot(t, bpsk, 'r-', 'LineWidth', 1.2);\n"
            "grid on; title('BPSK Modulated Waveform'); xlabel('Time (s)'); ylabel('Amplitude');\n\n"
            "disp('BPSK modulation completed.');\n"
        ),
        "expected_output": "BPSK modulation completed.",
        "viva_questions_json": [
            {"question": "What is the theoretical BER of BPSK over AWGN channel?", "answer": "P_b = Q(sqrt(2 * E_b / N_0))."},
            {"question": "How many bits per symbol does BPSK convey?", "answer": "BPSK conveys exactly 1 bit per symbol."}
        ]
    },
    # CONTROL: Step Response of Second-Order System
    {
        "category_code": "CONTROL",
        "title": "Second-Order System Transient Analysis",
        "slug": "second-order-step-response",
        "objective": "To determine transient specifications (Rise time, Peak time, Max overshoot, Settling time) for varied damping ratios (zeta).",
        "theory": "The standard closed-loop second-order transfer function is $T(s) = \\frac{\\omega_n^2}{s^2 + 2\\zeta \\omega_n s + \\omega_n^2}$.",
        "equations_json": ["T(s) = \\frac{\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}", "M_p = e^{-\\pi\\zeta / \\sqrt{1-\\zeta^2}} \\times 100\\%"],
        "procedure_json": ["Set natural frequency wn = 5 rad/s", "Define damping ratios: zeta = [0.2, 0.5, 0.707, 1.0]", "Compute analytic step response", "Overlay responses to observe overshoot vs damping"],
        "engine": "octave",
        "default_code": (
            "% Second-Order Step Response for Varied Damping Ratio\n"
            "clear all; close all; clc;\n\n"
            "wn = 5.0;\n"
            "t = 0:0.005:3;\n"
            "zetas = [0.2, 0.5, 0.707, 1.0];\n\n"
            "figure(1);\n"
            "hold on;\n"
            "for z = zetas\n"
            "    if z < 1.0\n"
            "        wd = wn * sqrt(1 - z^2);\n"
            "        phi = atan(sqrt(1 - z^2) / z);\n"
            "        y = 1.0 - (exp(-z * wn * t) / sqrt(1 - z^2)) .* sin(wd * t + phi);\n"
            "    else\n"
            "        y = 1.0 - exp(-wn * t) .* (1.0 + wn * t);\n"
            "    end\n"
            "    plot(t, y, 'LineWidth', 1.5);\n"
            "end\n"
            "hold off;\n"
            "grid on;\n"
            "title('Second-Order Step Response for Varied Damping Ratio \\zeta');\n"
            "xlabel('Time (s)'); ylabel('Amplitude');\n"
            "legend('\\zeta = 0.2', '\\zeta = 0.5', '\\zeta = 0.707', '\\zeta = 1.0');\n"
            "disp('Second order transient analysis plotted.');\n"
        ),
        "matlab_code": (
            "% Second-Order Step Response for Varied Damping Ratio\n"
            "clear all; close all; clc;\n\n"
            "wn = 5.0;\n"
            "t = 0:0.005:3;\n"
            "zetas = [0.2, 0.5, 0.707, 1.0];\n\n"
            "figure(1);\n"
            "hold on;\n"
            "for z = zetas\n"
            "    if z < 1.0\n"
            "        wd = wn * sqrt(1 - z^2);\n"
            "        phi = atan(sqrt(1 - z^2) / z);\n"
            "        y = 1.0 - (exp(-z * wn * t) / sqrt(1 - z^2)) .* sin(wd * t + phi);\n"
            "    else\n"
            "        y = 1.0 - exp(-wn * t) .* (1.0 + wn * t);\n"
            "    end\n"
            "    plot(t, y, 'LineWidth', 1.5);\n"
            "end\n"
            "hold off;\n"
            "grid on;\n"
            "title('Second-Order Step Response for Varied Damping Ratio \\zeta');\n"
            "xlabel('Time (s)'); ylabel('Amplitude');\n"
            "legend('\\zeta = 0.2', '\\zeta = 0.5', '\\zeta = 0.707', '\\zeta = 1.0');\n"
            "disp('Second order transient analysis plotted.');\n"
        ),
        "expected_output": "Second order transient analysis plotted.",
        "viva_questions_json": [
            {"question": "What is the relationship between damping ratio and percentage overshoot?", "answer": "As damping ratio increases, percentage overshoot decreases exponentially until zeta >= 1 where there is no overshoot."},
            {"question": "What damping ratio provides the optimal compromise between rise time and settling time?", "answer": "zeta = 0.707 (optimal damping) provides minimal settling time with under 5% overshoot."}
        ]
    },
    # CONTROL: PID Controller Tuning
    {
        "category_code": "CONTROL",
        "title": "Closed-Loop PID Controller Simulation",
        "slug": "pid-controller-tuning",
        "objective": "To implement proportional, integral, and derivative control and evaluate steady-state error reduction.",
        "theory": "The PID control law is $u(t) = K_p e(t) + K_i \\int_0^t e(\\tau)d\\tau + K_d \\frac{de(t)}{dt}$.",
        "equations_json": ["u(t) = K_p e(t) + K_i \\int e dt + K_d \\frac{de}{dt}", "E(s) = R(s) - Y(s)"],
        "procedure_json": ["Model first order plant", "Apply discrete PID loop", "Simulate response and verify zero steady-state error"],
        "engine": "octave",
        "default_code": (
            "% Closed-Loop PID Controller Simulation\n"
            "clear all; close all; clc;\n\n"
            "dt = 0.01; N = 500;\n"
            "t = (0:N-1) * dt;\n"
            "setpoint = 1.0;\n"
            "Kp = 15.0; Ki = 25.0; Kd = 1.2;\n\n"
            "y = zeros(1, N); e_int = 0.0; e_prev = 0.0;\n"
            "for k = 1:N-1\n"
            "    e = setpoint - y(k);\n"
            "    e_int = e_int + e * dt;\n"
            "    e_der = (e - e_prev) / dt;\n"
            "    u = Kp * e + Ki * e_int + Kd * e_der;\n"
            "    y(k+1) = y(k) + dt * (-2.0 * y(k) + 0.5 * u);\n"
            "    e_prev = e;\n"
            "end\n\n"
            "figure(1);\n"
            "plot(t, y, 'b-', 'LineWidth', 2);\n"
            "hold on;\n"
            "plot([0 t(end)], [setpoint setpoint], 'r--', 'LineWidth', 1.5);\n"
            "hold off;\n"
            "grid on;\n"
            "title('PID Closed-Loop Step Response');\n"
            "xlabel('Time (s)'); ylabel('Amplitude');\n"
            "legend('PID Output y(t)', 'Setpoint');\n"
            "disp('PID simulation completed successfully.');\n"
        ),
        "matlab_code": (
            "% Closed-Loop PID Controller Simulation\n"
            "clear all; close all; clc;\n\n"
            "dt = 0.01; N = 500;\n"
            "t = (0:N-1) * dt;\n"
            "setpoint = 1.0;\n"
            "Kp = 15.0; Ki = 25.0; Kd = 1.2;\n\n"
            "y = zeros(1, N); e_int = 0.0; e_prev = 0.0;\n"
            "for k = 1:N-1\n"
            "    e = setpoint - y(k);\n"
            "    e_int = e_int + e * dt;\n"
            "    e_der = (e - e_prev) / dt;\n"
            "    u = Kp * e + Ki * e_int + Kd * e_der;\n"
            "    y(k+1) = y(k) + dt * (-2.0 * y(k) + 0.5 * u);\n"
            "    e_prev = e;\n"
            "end\n\n"
            "figure(1);\n"
            "plot(t, y, 'b-', 'LineWidth', 2);\n"
            "hold on;\n"
            "plot([0 t(end)], [setpoint setpoint], 'r--', 'LineWidth', 1.5);\n"
            "hold off;\n"
            "grid on;\n"
            "title('PID Closed-Loop Step Response');\n"
            "xlabel('Time (s)'); ylabel('Amplitude');\n"
            "legend('PID Output y(t)', 'Setpoint');\n"
            "disp('PID simulation completed successfully.');\n"
        ),
        "expected_output": "PID simulation completed successfully.",
        "viva_questions_json": [
            {"question": "What is the primary role of the Integral term in a PID controller?", "answer": "The Integral term accumulates past errors to eliminate steady-state error."},
            {"question": "What is derivative kick and how is it avoided in PID implementation?", "answer": "Derivative kick occurs when a step change in setpoint produces an infinite derivative; it is avoided by differentiating process output y(t) instead of error e(t)."}
        ]
    }
]

EXPERIMENTS = DSP_EXPERIMENTS + OTHER_EXPERIMENTS
