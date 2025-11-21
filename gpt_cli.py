from __future__ import annotations
import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from gpt_design import GPTDesign, policy_from_summary_meta, export_particle  # type: ignore[attr-defined]

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_once(prompt: str, evidence_source: Optional[str] = None) -> Dict[str, Any]:
    # ポリシーを meta/summary_meta.json から読み込み
    policy = policy_from_summary_meta()
    logger.info(
        "Policy loaded: mode=%s threshold=%s require_evidence=%s",
        getattr(policy, "mode", "unknown"),
        getattr(policy, "threshold", "n/a"),
        getattr(policy, "require_evidence", False),
    )

    gpt = GPTDesign(
        threshold=getattr(policy, "threshold", 0.90),
        require_evidence=getattr(policy, "require_evidence", False),
    )

    evidence: Optional[Dict[str, Any]] = None
    if evidence_source:
        evidence = {"source": evidence_source}

    result = gpt.generate(prompt, evidence=evidence)
    reply = result["reply"]
    evalr = result["evaluation"]
    px = result["particle"]

    saved_path: Optional[str] = None
    storage_commit_id: Optional[str] = None

    if export_particle is not None:
        out_path = export_particle(
            text=px["Raw Text"],
            evaluation={
                "score": px["Reliability Score"],
                "status": px["Processing Outcome"],
            },
            true_intent=px["True Intent"],
            evidence_sources=px["Evidence Sources"],
            parent_commit=px["Parent Commit"],
        )
        saved_path = str(out_path)
        storage_commit_id = Path(out_path).stem
        logger.info("Particle saved: %s", saved_path)
    else:
        logger.warning("export_particle is not available; particle not persisted.")

    return {
        "answer": reply,
        "evaluation": evalr,
        "true_intent": px["True Intent"],
        "particle_meta": {
            # gpt_design 内部で付与した UUID
            "internal_commit_uuid": px["Commit ID"],
            # 粒子ファイル名 = V1 粒子の 'Commit ID'
            "storage_commit_id": storage_commit_id,
            "processing_outcome": px["Processing Outcome"],
            "saved_path": saved_path,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hallucination-resistant GPT CLI (particle-emitting)."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="評価したいプロンプト。省略時は対話的に入力。",
    )
    parser.add_argument(
        "--evidence-source",
        "-e",
        help="証拠ソースのラベル（例: meta/summary_meta.json, user）。",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="結果を JSON で出力する（デフォルト）。",
    )

    args = parser.parse_args()

    if args.prompt:
        prompt = args.prompt
    else:
        prompt = input("Prompt> ").strip()

    result = run_once(prompt, evidence_source=args.evidence_source)

    # デフォルトは JSON 出力
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
