FROM python:3.12-slim

WORKDIR /app

# Install GNU Octave, gnuplot, fonts, and system build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    octave \
    octave-signal \
    octave-control \
    gnuplot \
    fonts-freefont-ttf \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir reportlab celery redis pydantic

COPY . /app/execution_worker
WORKDIR /app

ENV PYTHONPATH=/app

CMD ["python", "-m", "execution_worker.worker"]
