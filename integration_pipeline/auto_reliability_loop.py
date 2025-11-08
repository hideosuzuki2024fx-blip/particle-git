import subprocess, time, logging
from datetime import datetime

logging.basicConfig(filename="auto_pipeline.log", level=logging.INFO, format="[%(asctime)s] %(message)s")

def run_pipeline():
    steps = [
        "python particle_exporter.py",
        "python integration_pipeline/pipeline_controller.py",
        "python integration_pipeline/optimizer.py"
    ]
    for step in steps:
        logging.info(f"Executing: {step}")
        subprocess.run(step, shell=True)
        time.sleep(2)
    logging.info("Cycle complete. Waiting for next iteration...")

def main():
    logging.info("Starting continuous reliability loop...")
    while True:
        run_pipeline()
        time.sleep(3600)  # every 1 hour

if __name__ == "__main__":
    main()
