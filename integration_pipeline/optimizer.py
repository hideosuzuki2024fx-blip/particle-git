import json
from pathlib import Path
from statistics import mean

# optimizer.py
# Purpose: Analyze particle data and integration report to derive
# optimization recommendations for GPT output reliability.

REPORT_PATH = Path("../integration_report.json")
PARTICLE_DIR = Path("../particle-git/particles")
OPTIMIZED_PATH = Path("optimization_summary.json")

def load_report() -> dict:
    if REPORT_PATH.exists():
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    return {}

def analyze_particles() -> list[float]:
    scores = []
    for p in PARTICLE_DIR.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            scores.append(data.get("Reliability Score", 0))
        except Exception:
            continue
    return scores

def derive_recommendations(avg_score: float) -> list[str]:
    recs = []
    if avg_score < 0.7:
        recs.append("Increase evidence verification weight.")
        recs.append("Reduce speculation tolerance.")
    elif avg_score < 0.9:
        recs.append("Maintain scoring balance; emphasize intent clarity.")
    else:
        recs.append("Current weighting is optimal. Continue monitoring.")
    return recs

def main():
    report = load_report()
    scores = analyze_particles()
    avg_local = round(mean(scores), 4) if scores else 0.0
    combined = {
        "report_average": report.get("average_score", 0.0),
        "local_average": avg_local,
        "recommendations": derive_recommendations(avg_local)
    }
    OPTIMIZED_PATH.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[optimizer] Optimization summary saved: {OPTIMIZED_PATH.resolve()}")

if __name__ == "__main__":
    main()
