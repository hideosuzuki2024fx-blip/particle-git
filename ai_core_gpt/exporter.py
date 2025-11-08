from __future__ import annotations
"""
particle_exporter.py

Phase 2: Integration-ready version.
Adds pipeline hooks for unified GPT evaluation workflow, enabling
automatic chaining between reliability scoring, particle export, and
downstream analysis modules.
"""

import json
import re
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, Optional, Callable

LOG_FILE = Path("particle_export.log")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

PARTICLE_DIR = Path("particles")

try:
    from reliability_evaluator import compute_reliability_score  # type: ignore
except ModuleNotFoundError:
    @dataclass
    class _EvalResult:
        score: float
        bonuses: Dict[str, float]
        penalties: Dict[str, float]
        diagnostic: str
        status: str

    _DEFAULT_WEIGHTS = {
        "no_emotional": 0.15,
        "no_speculation": 0.15,
        "has_evidence": 0.20,
        "clear_intent": 0.15,
        "length_ok": 0.10,
        "no_contradiction": 0.25,
    }
    _META_PENALTIES = {
        "emotional": -0.10,
        "missing_evidence": -0.15,
        "contradiction": -0.20,
        "true_intent_bonus": +0.10,
    }

    def compute_reliability_score(
        text: str,
        has_evidence: bool = False,
        true_intent_clear: bool = False,
        contradiction: bool = False,
        threshold: float = 0.90,
    ) -> _EvalResult:
        score = 0.0
        bonuses: Dict[str, float] = {}
        penalties: Dict[str, float] = {}

        if not re.search(r"おそらく|たぶん|と思われ|感じ|hope|maybe|probably", text):
            score += _DEFAULT_WEIGHTS["no_emotional"]
            bonuses["no_emotional"] = _DEFAULT_WEIGHTS["no_emotional"]
        else:
            penalties["emotional"] = _META_PENALTIES["emotional"]

        if not re.search(r"推測|予想|かもしれ|guess|speculat", text):
            score += _DEFAULT_WEIGHTS["no_speculation"]
            bonuses["no_speculation"] = _DEFAULT_WEIGHTS["no_speculation"]

        if has_evidence:
            score += _DEFAULT_WEIGHTS["has_evidence"]
            bonuses["has_evidence"] = _DEFAULT_WEIGHTS["has_evidence"]
        else:
            penalties["missing_evidence"] = _META_PENALTIES["missing_evidence"]

        if true_intent_clear:
            score += _DEFAULT_WEIGHTS["clear_intent"] + _META_PENALTIES["true_intent_bonus"]
            bonuses["clear_intent"] = _DEFAULT_WEIGHTS["clear_intent"] + _META_PENALTIES["true_intent_bonus"]

        if len(text) > 10:
            score += _DEFAULT_WEIGHTS["length_ok"]
            bonuses["length_ok"] = _DEFAULT_WEIGHTS["length_ok"]

        if not contradiction:
            score += _DEFAULT_WEIGHTS["no_contradiction"]
            bonuses["no_contradiction"] = _DEFAULT_WEIGHTS["no_contradiction"]
        else:
            penalties["contradiction"] = _META_PENALTIES["contradiction"]

        score = round(max(min(score + sum(penalties.values()), 1.0), 0.0), 3)
        status = "promoted" if score >= threshold else "record_only"
        diag = f"Final score={score}, threshold={threshold}, status={status}"
        return _EvalResult(score, bonuses, penalties, diag, status)

def _ensure_path(base: Path) -> Path:
    try:
        base.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Ensured directory exists: {base}")
    except Exception:
        logging.exception(f"Failed to create directory {base}")
        raise
    return base

def export_particle(
    text: str,
    evaluation: Dict[str, Any],
    true_intent: Dict[str, str],
    evidence_sources: Optional[list[str]] = None,
    parent_commit: Optional[str] = None,
    now: Optional[datetime] = None,
    post_hook: Optional[Callable[[Path], None]] = None,
) -> Path:
    ts = (now or datetime.now(UTC))
    year, month = ts.strftime("%Y"), ts.strftime("%m")
    folder = _ensure_path(PARTICLE_DIR / year / month)

    particle_type = "EVAL_" if evaluation.get("status") == "record_only" else "AUTO_"
    uid = uuid.uuid4().hex[:6]
    filename = f"{particle_type}{ts.strftime('%Y%m%d_%H%M%S')}_{uid}.json"
    path = folder / filename

    logging.info(f"Exporting particle to {path}")

    data = {
        "Commit ID": str(uuid.uuid4()),
        "Parent Commit": parent_commit or "root",
        "True Intent": true_intent,
        "Reliability Score": evaluation.get("score", 0.0),
        "Raw Text": text,
        "Context ID": f"CTX_{ts.strftime('%Y%m%d%H%M%S')}",
        "Processing Outcome": evaluation.get("status"),
        "Evidence Sources": evidence_sources or [],
        "Reviewer": "parent-gpt",
        "Score History": [
            {
                "version": "V1.1",
                "score": evaluation.get("score", 0.0),
                "timestamp": ts.isoformat(),
            }
        ],
        "Conflict Status": "pending",
    }

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Particle JSON saved successfully: {path}")
    except Exception:
        logging.exception("Failed to export particle JSON")
        raise

    if post_hook:
        try:
            post_hook(path)
            logging.info(f"Post-hook executed for {path}")
        except Exception:
            logging.exception(f"Post-hook failed for {path}")

    return path

def _self_test() -> None:
    logging.info("Running self-tests...")
    res1 = compute_reliability_score(
        "This has evidence and a clear intent with no contradiction.",
        has_evidence=True,
        true_intent_clear=True,
        contradiction=False,
        threshold=0.90,
    )
    p1 = export_particle(
        text="ok-1",
        evaluation=getattr(res1, "__dict__", dict(score=res1.score, status=res1.status)),
        true_intent={"Category": "Reliability Framework", "Details": "self-test 1"},
        evidence_sources=["meta/summary_meta.json"],
    )
    assert p1.name.startswith("AUTO_"), f"Expected AUTO_ prefix, got {p1.name}"

    res2 = compute_reliability_score(
        "maybe",
        has_evidence=False,
        true_intent_clear=False,
        contradiction=False,
        threshold=0.99,
    )
    p2 = export_particle(
        text="ok-2",
        evaluation=getattr(res2, "__dict__", dict(score=res2.score, status=res2.status)),
        true_intent={"Category": "Meta Evaluation", "Details": "self-test 2"},
        evidence_sources=[],
    )
    assert p2.name.startswith("EVAL_"), f"Expected EVAL_ prefix, got {p2.name}"

    logging.info(f"Self-tests passed: {p1}, {p2}")

def main() -> None:
    logging.info("Running integration demo export...")

    def announce_export(path: Path) -> None:
        logging.info(f"[Pipeline] Particle ready for downstream: {path}")

    demo_text = "System achieved 0.95 reliability with verified evidence."
    eval_result = compute_reliability_score(
        demo_text, has_evidence=True, true_intent_clear=True
    )
    intent = {"Category": "Reliability Framework", "Details": "Scoring result storage test"}

    saved_path = export_particle(
        text=demo_text,
        evaluation=getattr(eval_result, "__dict__", dict(score=eval_result.score, status=eval_result.status)),
        true_intent=intent,
        evidence_sources=["meta/summary_meta.json"],
        post_hook=announce_export,
    )
    logging.info(f"Particle exported to: {saved_path}")

if __name__ == "__main__":
    _self_test()
    main()
