from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

META_DIR = Path("meta")
SUMMARY_META = META_DIR / "summary_meta.json"


@dataclass
class ReasoningPolicy:
    mode: str = "balanced"
    threshold: float = 0.90
    require_evidence: bool = False
    hedging_language: bool = True
    factual_density: str = "normal"
    emotional_tone: str = "neutral"
    meta_snapshot: dict[str, Any] | None = None
    diagnostic: str = ""


def policy_from_summary_meta(path: Optional[Path] = None) -> ReasoningPolicy:
    """
    meta/summary_meta.json からポリシーをロードする。
    - ファイル無し → デフォルト
    - JSON 読み込み失敗 → デフォルト
    """
    meta_path = path or SUMMARY_META

    if not meta_path.exists():
        return ReasoningPolicy(
            diagnostic=f"{meta_path} not found; using defaults"
        )

    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Failed to load %s: %s", meta_path, e)
        return ReasoningPolicy(
            diagnostic=f"{meta_path} load error; using defaults: {e}"
        )

    # summary_meta.json の構造は柔らかく解釈する
    policy = data.get("policy", {})
    mode = data.get("mode") or policy.get("mode") or "balanced"
    threshold = data.get("threshold") or policy.get("threshold") or 0.90
    require_evidence = (
        data.get("require_evidence") or policy.get("require_evidence") or False
    )
    hedging_language = data.get("hedging_language", True)
    factual_density = data.get("factual_density", "normal")
    emotional_tone = data.get("emotional_tone", "neutral")

    return ReasoningPolicy(
        mode=str(mode),
        threshold=float(threshold),
        require_evidence=bool(require_evidence),
        hedging_language=bool(hedging_language),
        factual_density=str(factual_density),
        emotional_tone=str(emotional_tone),
        meta_snapshot=data,
        diagnostic=f"loaded from {meta_path}",
    )
