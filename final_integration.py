import subprocess, logging, time
from datetime import datetime, timezone

logging.basicConfig(filename="final_integration.log", level=logging.INFO, format="[%(asctime)s] %(message)s")

def run_all():
    steps = [
        "python particle_exporter.py",
        "python integration_pipeline/pipeline_controller.py",
        "python integration_pipeline/optimizer.py",
        "python gpt_design.py"
    ]
    for step in steps:
        logging.info(f"Running {step}")
        subprocess.run(step, shell=True)
        time.sleep(2)
    logging.info("Final GPT integration pipeline completed successfully.")

if __name__ == "__main__":
    logging.info("=== Starting Final GPT Integration Cycle ===")
    run_all()
    logging.info("=== Integration Complete ===")
