import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# pipeline_controller.py
# Integration pipeline controller:
# Collects recent particles, aggregates reliability scores,
# and generates a summary report for model evaluation.

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("integration_pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

PARTICLE_DIR = Path("../particle-git/particles")
REPORT_PATH = Path("integration_report.json")

def collect_particles() -> list[Path]:
    """Recursively collect all particle JSON files."""
    particles = sorted(PARTICLE_DIR.rglob("*.json"))
    logging.info(f"Collected {len(particles)} particle files.")
    return particles

def aggregate_scores(particles: list[Path]) -> dict:
    """Aggregate reliability scores and statuses."""
    scores, promoted, record_only = [], 0, 0
    for p in particles:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            score = data.get("Reliability Score", 0.0)
            status = data.get("Processing Outcome", "unknown")
            scores.append(score)
            if status == "promoted":
                promoted += 1
            elif status == "record_only":
                record_only += 1
        except Exception as e:
            logging.error(f"Failed to read {p}: {e}")
    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    return {
        "total_particles": len(scores),
        "average_score": avg_score,
        "promoted_count": promoted,
        "record_only_count": record_only,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }

def export_report(summary: dict) -> Path:
    """Save aggregated report as JSON."""
    REPORT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info(f"Integration report saved: {REPORT_PATH.resolve()}")
    return REPORT_PATH

def main() -> None:
    logging.info("Running integration pipeline controller...")
    particles = collect_particles()
    summary = aggregate_scores(particles)
    export_report(summary)
    logging.info(f"Summary: {summary}")

if __name__ == "__main__":
    main()
