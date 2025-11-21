from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
import json
import uuid
import logging

logger = logging.getLogger(__name__)

PARTICLE_ROOT = Path("particles")


def export_particle(
    *,
    text: str,
    evaluation: Dict[str, Any],
    true_intent: Dict[str, Any],
    evidence_sources: List[str],
    parent_commit: str,
) -> Path:
    """
    V1 粒子スキーマで JSON を保存するエクスポータ。

    出力例（キー構造）は AUTO_1761956191.json などの既存粒子に揃える：

    {
      "Commit ID": "AUTO_YYYYMMDD_HHMMSS_xxx",
      "Parent Commit": "...",
      "True Intent": { "Category": "...", "Details": "..." },
      "Reliability Score": 0.93,
      "Raw Text": "...",
      "Context ID": "CTX_YYYYMMDDHHMMSS",
      "Processing Outcome": "promoted / record_only など",
      "Evidence Sources": [],
      "Reviewer": "gpt-design",
      "Score History": [
        { "version": "DESIGN-1.1", "score": 0.93, "timestamp": "..." }
      ],
      "Conflict Status": "pending"
    }
    """
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    dir_path = PARTICLE_ROOT / year / month
    dir_path.mkdir(parents=True, exist_ok=True)

    ts = now.strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:6]
    commit_id = f"AUTO_{ts}_{suffix}"
    filename = f"{commit_id}.json"
    out_path = dir_path / filename

    score = float(evaluation.get("score", 0.0))
    status = str(evaluation.get("status", "record_only"))

    particle: Dict[str, Any] = {
        "Commit ID": commit_id,
        "Parent Commit": parent_commit,
        "True Intent": true_intent,
        "Reliability Score": score,
        "Raw Text": text,
        "Context ID": f"CTX_{ts}",
        "Processing Outcome": status,
        "Evidence Sources": evidence_sources or [],
        "Reviewer": "gpt-design",
        "Score History": [
            {
                "version": "DESIGN-1.1",
                "score": score,
                "timestamp": now.isoformat(),
            }
        ],
        "Conflict Status": "pending",
    }

    out_path.write_text(
        json.dumps(particle, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Particle exported (V1 schema): %s", out_path)
    return out_path
