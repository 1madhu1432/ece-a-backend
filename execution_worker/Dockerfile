FROM python:3.12-slim

WORKDIR /app

# Install GNU Octave, gnuplot, fonts, and system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    octave \
    octave-signal \
    octave-control \
    gnuplot \
    fonts-freefont-ttf \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy scipy sympy matplotlib pandas reportlab celery redis pydantic

COPY . /app/execution_worker
WORKDIR /app

ENV PYTHONPATH=/app

CMD ["python", "-c", "print('ECE AI Studio Execution Sandbox Worker Online')"]
