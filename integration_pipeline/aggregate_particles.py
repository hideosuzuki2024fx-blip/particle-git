from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple, List
import json
import datetime

PARTICLE_ROOT = Path("particles")
SUMMARY_DIR = Path("summary")
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = SUMMARY_DIR / "particles_summary.json"


def load_particles() -> List[Tuple[Path, Dict[str, Any]]]:
    particles: List[Tuple[Path, Dict[str, Any]]] = []
    if not PARTICLE_ROOT.exists():
        return particles

    for path in PARTICLE_ROOT.rglob("AUTO_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            particles.append((path, data))
        except Exception:
            # 壊れた JSON は無視
            continue
    return particles


def main() -> None:
    particles = load_particles()
    total = len(particles)

    intents: Dict[str, Dict[str, Any]] = {}
    status_counts: Dict[str, int] = {}

    for path, p in particles:
        score = float(p.get("Reliability Score", 0.0))
        status = str(p.get("Processing Outcome", "unknown"))

        ti = p.get("True Intent") or {}
        category = str(ti.get("Category") or "Unknown")

        # status 集計
        status_counts[status] = status_counts.get(status, 0) + 1

        # intentごとの集計
        info = intents.setdefault(
            category,
            {"count": 0, "avg_score": 0.0, "promoted": 0, "record_only": 0},
        )
        info["count"] += 1
        info["avg_score"] += score
        if status == "promoted":
            info["promoted"] += 1
        elif status == "record_only":
            info["record_only"] += 1

    # 平均スコア計算
    for cat, info in intents.items():
        if info["count"]:
            info["avg_score"] = round(info["avg_score"] / info["count"], 3)

    summary = {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_particles": total,
        "status_counts": status_counts,
        "intents": intents,
    }

    OUT_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote summary to {OUT_PATH}")


if __name__ == "__main__":
    main()
