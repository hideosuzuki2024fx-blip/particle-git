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
    粒子 JSON を particles/YYYY/MM/AUTO_*.json として保存する。
    gpt_design.GPTDesign.generate() から呼ばれる前提。
    """
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    dir_path = PARTICLE_ROOT / year / month
    dir_path.mkdir(parents=True, exist_ok=True)

    ts = now.strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:6]
    filename = f"AUTO_{ts}_{suffix}.json"
    out_path = dir_path / filename

    payload = {
        "particle_id": f"AUTO-{ts}-{suffix}",
        "created_at": now.isoformat(),
        "parent_commit": parent_commit,
        "text": text,
        "evaluation": evaluation,
        "true_intent": true_intent,
        "evidence_sources": evidence_sources,
    }

    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Particle exported: %s", out_path)
    return out_path
