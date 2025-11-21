from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


def _load_current_policy(meta_dir: Path) -> Dict[str, Any]:
    """meta/summary_meta.json から現在のポリシーを読み込む。存在しない場合は厳しめのデフォルト。"""
    meta_file = meta_dir / "summary_meta.json"
    if not meta_file.exists():
        return {
            "mode": "strict",
            "threshold": 0.9,
            "require_evidence": True,
            "hedging_language": False,
            "factual_density": "high",
            "emotional_tone": "neutral",
            "source": "default",
        }

    try:
        data = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {
            "mode": "strict",
            "threshold": 0.9,
            "require_evidence": True,
            "hedging_language": False,
            "factual_density": "high",
            "emotional_tone": "neutral",
            "source": f"load_error: {e}",
        }

    policy = data.get("policy", {})
    return {
        "mode": data.get("mode") or policy.get("mode") or "strict",
        "threshold": float(data.get("threshold") or policy.get("threshold") or 0.9),
        "require_evidence": bool(
            data.get("require_evidence") or policy.get("require_evidence") or True
        ),
        "hedging_language": bool(data.get("hedging_language", False)),
        "factual_density": str(data.get("factual_density", "high")),
        "emotional_tone": str(data.get("emotional_tone", "neutral")),
        "source": str(data.get("source", "summary_meta.json")),
    }


def _iter_particle_files(particles_root: Path):
    if not particles_root.exists():
        return []
    return list(particles_root.rglob("AUTO_*.json"))


def _normalize_particle(raw: Dict[str, Any], path: Path) -> Dict[str, Any]:
    """
    粒子 JSON を内部共通形式に正規化する。

    実際のファイルから確認できた形式をカバー：
    - V1 スキーマ（"Commit ID", "Reliability Score", "Processing Outcome", "True Intent" など）
    - 旧形式（particle_id + evaluation + true_intent + text）
    """
    # V1 スキーマ（今回のセッションで生成された粒子）
    if "Reliability Score" in raw:
        score = float(raw.get("Reliability Score", 0.0))
        status = str(raw.get("Processing Outcome", "record_only"))
        true_intent = raw.get("True Intent", {}) or {}
        intent_cat = str(true_intent.get("Category", "Unknown"))
        intent_details = str(true_intent.get("Details", ""))

        created_at = None
        history = raw.get("Score History") or []
        if history and isinstance(history, list):
            ts = history[0].get("timestamp")
            if isinstance(ts, str):
                created_at = ts

        commit_id = str(raw.get("Commit ID", path.stem))
        return {
            "commit_id": commit_id,
            "score": score,
            "status": status,
            "intent_category": intent_cat,
            "intent_details": intent_details,
            "created_at": created_at,
            "path": str(path),
        }

    # 旧形式（ログに残っている AUTO_1761... など）
    if "evaluation" in raw and "true_intent" in raw:
        eval_block = raw.get("evaluation") or {}
        true_intent = raw.get("true_intent") or {}
        score = float(eval_block.get("score", 0.0))
        status = str(eval_block.get("status", "record_only"))
        intent_cat = str(true_intent.get("Category", "Unknown"))
        intent_details = str(true_intent.get("Details", ""))
        created_at = raw.get("created_at")
        commit_id = str(raw.get("particle_id", path.stem))

        return {
            "commit_id": commit_id,
            "score": score,
            "status": status,
            "intent_category": intent_cat,
            "intent_details": intent_details,
            "created_at": created_at,
            "path": str(path),
        }

    # それ以外は最低限の情報だけ残す
    return {
        "commit_id": str(raw.get("Commit ID") or raw.get("particle_id") or path.stem),
        "score": float(raw.get("score", 0.0)),
        "status": str(raw.get("status", "unknown")),
        "intent_category": str(raw.get("intent", "Unknown")),
        "intent_details": "",
        "created_at": raw.get("created_at"),
        "path": str(path),
    }


def _load_particles(particles_root: Path) -> List[Dict[str, Any]]:
    particles: List[Dict[str, Any]] = []
    for fp in _iter_particle_files(particles_root):
        try:
            raw = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        norm = _normalize_particle(raw, fp)
        particles.append(norm)
    return particles


def _aggregate(particles: List[Dict[str, Any]]) -> Dict[str, Any]]:
    total = len(particles)
    status_counts: Dict[str, int] = {}
    intent_stats: Dict[str, Dict[str, Any]] = {}

    total_score = 0.0

    for p in particles:
        score = float(p.get("score", 0.0))
        status = str(p.get("status", "unknown"))
        intent = str(p.get("intent_category", "Unknown"))

        total_score += score
        status_counts[status] = status_counts.get(status, 0) + 1

        s = intent_stats.setdefault(
            intent,
            {"count": 0, "score_sum": 0.0, "promoted": 0, "record_only": 0},
        )
        s["count"] += 1
        s["score_sum"] += score
        if status == "promoted":
            s["promoted"] += 1
        elif status == "record_only":
            s["record_only"] += 1

    avg_score = total_score / total if total else 0.0

    intents_out: Dict[str, Any] = {}
    for name, s in intent_stats.items():
        c = s["count"]
        intents_out[name] = {
            "count": c,
            "avg_score": (s["score_sum"] / c) if c else 0.0,
            "promoted": s["promoted"],
            "record_only": s["record_only"],
        }

    return {
        "total_particles": total,
        "avg_score": avg_score,
        "status_counts": status_counts,
        "intents": intents_out,
    }


def _recommend_policy(
    aggregate: Dict[str, Any], current: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    """
    シンプルなヒューリスティックでポリシー推奨値を計算する。

    - 平均スコアが current.threshold よりかなり低い → しきい値を少し上げる
    - 平均スコアが current.threshold よりかなり高い → しきい値を少し下げる
    - promoted 比率が極端に低い / 高い場合は mode を調整する
    """
    total = aggregate.get("total_particles", 0) or 0
    avg_score = float(aggregate.get("avg_score", 0.0))
    status_counts = aggregate.get("status_counts", {}) or {}

    current_threshold = float(current.get("threshold", 0.9))
    mode = str(current.get("mode", "strict"))
    require_evidence = bool(current.get("require_evidence", True))

    promoted = status_counts.get("promoted", 0)
    record_only = status_counts.get("record_only", 0)
    promoted_ratio = promoted / total if total else 0.0
    record_only_ratio = record_only / total if total else 0.0

    # しきい値の調整
    recommended_threshold = current_threshold
    explanation_parts = []

    # current_threshold よりかなり低い（品質が低い）
    if avg_score < current_threshold - 0.05:
        recommended_threshold = min(0.99, current_threshold + 0.05)
        explanation_parts.append(
            f"平均スコア {avg_score:.3f} が現在の threshold {current_threshold:.3f} より低いため、"
            "しきい値をやや引き上げることを推奨します。"
        )
    # current_threshold よりかなり高い（かなり保守的すぎる）
    elif avg_score > current_threshold + 0.05:
        recommended_threshold = max(0.7, current_threshold - 0.05)
        explanation_parts.append(
            f"平均スコア {avg_score:.3f} が現在の threshold {current_threshold:.3f} を安定して上回っているため、"
            "しきい値をやや引き下げる余地があります。"
        )
    else:
        explanation_parts.append(
            f"平均スコア {avg_score:.3f} は現在の threshold {current_threshold:.3f} に近いため、"
            "threshold は現状維持を推奨します。"
        )

    # mode の調整
    recommended_mode = mode
    if promoted_ratio < 0.3:
        recommended_mode = "strict"
        explanation_parts.append(
            f"promoted 比率が低い ({promoted_ratio:.2%}) ため、strict モード継続を推奨します。"
        )
    elif promoted_ratio > 0.7 and avg_score > current_threshold:
        recommended_mode = "balanced"
        explanation_parts.append(
            f"promoted 比率が高い ({promoted_ratio:.2%}) かつ平均スコアも高いため、"
            "balanced モードへの緩和を検討できます。"
        )
    else:
        explanation_parts.append(
            f"promoted 比率 {promoted_ratio:.2%} と record_only 比率 {record_only_ratio:.2%} は極端ではないため、"
            "mode は現状維持とします。"
        )

    # require_evidence は原則維持（ログから自動で弱めない）
    recommended_require_evidence = require_evidence
    if require_evidence:
        explanation_parts.append(
            "require_evidence は True のまま維持します（ログから自動的に緩和はしません）。"
        )
    else:
        explanation_parts.append(
            "require_evidence は False ですが、平均スコアや record_only の傾向に応じて手動で見直してください。"
        )

    explanation = "\n".join(explanation_parts)

    recommended = {
        "mode": recommended_mode,
        "threshold": recommended_threshold,
        "require_evidence": recommended_require_evidence,
        "hedging_language": current.get("hedging_language", False),
        "factual_density": current.get("factual_density", "high"),
        "emotional_tone": current.get("emotional_tone", "neutral"),
    }
    return recommended, explanation


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    particles_root = repo_root / "particles"
    meta_dir = repo_root / "meta"
    summary_dir = repo_root / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    current_policy = _load_current_policy(meta_dir)
    particles = _load_particles(particles_root)
    aggregate = _aggregate(particles)
    recommended_policy, explanation = _recommend_policy(aggregate, current_policy)

    out = {
        "generated_at": now.isoformat(),
        "particle_source_root": str(particles_root),
        "total_particles": aggregate.get("total_particles", 0),
        "avg_score": aggregate.get("avg_score", 0.0),
        "status_counts": aggregate.get("status_counts", {}),
        "intent_stats": aggregate.get("intents", {}),
        "current_policy": current_policy,
        "recommended_policy": recommended_policy,
        "policy_explanation": explanation,
    }

    # 旧チャットの設計では optimization_summary.json をリポジトリ直下に置いていた。
    # 現在は summary/ も存在するので、両方に書き出して互換性を保つ。
    out_root = repo_root / "optimization_summary.json"
    out_summary = summary_dir / "optimization_summary.json"

    out_root.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    out_summary.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Optimization summary written to {out_root}")
    print(f"Optimization summary written to {out_summary}")


if __name__ == "__main__":
    main()
