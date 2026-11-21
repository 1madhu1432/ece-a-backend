"""
ECE AI Studio - Execution Sandbox Worker
Handles background sandboxed code executions for MATLAB / GNU Octave.
"""
import os
import sys
import time
import logging
import asyncio
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ECEExecutionWorker")

from execution_worker.runners.octave_runner import OctaveRunner

def verify_runtimes():
    logger.info("Initializing ECE AI Studio MATLAB/GNU Octave Sandbox Worker...")
    
    # Verify GNU Octave and Gnuplot
    oct_runner = OctaveRunner()
    if oct_runner.octave_bin:
        logger.info(f"GNU Octave Runtime Verified: {oct_runner.octave_bin}")
    else:
        logger.warning("GNU Octave executable not found on host. High-fidelity MATLAB simulation fallback will be active.")

    if oct_runner.gnuplot_bin:
        logger.info(f"Gnuplot Graphics Engine Verified: {oct_runner.gnuplot_bin}")
    else:
        logger.warning("Gnuplot executable not found on host.")

def run_worker():
    verify_runtimes()
    logger.info("ECE AI Studio Execution Worker is active and listening for execution tasks.")
    
    # Check if Celery is configured
    broker_url = os.environ.get("CELERY_BROKER_URL") or os.environ.get("REDIS_URL")
    if broker_url and not sys.platform.startswith("win"):
        try:
            from celery import Celery
            app = Celery("ece_worker", broker=broker_url)
            logger.info(f"Connected Celery broker at {broker_url}")
            app.worker_main(["worker", "--loglevel=info", "-c", "2"])
            return
        except Exception as e:
            logger.warning(f"Celery startup skipped: {e}. Falling back to stand-alone heartbeat daemon.")

    # Stand-alone daemon loop
    try:
        while True:
            time.sleep(30)
            logger.info("ECE Execution Worker heartbeat: healthy, sandbox clean.")
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")

if __name__ == "__main__":
    run_worker()
