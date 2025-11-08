from __future__ import annotations
# gpt_design.py — Hallucination-Resistant GPT Design (self-contained)
import json, re, logging, uuid
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# ---- Optional imports with graceful fallbacks --------------------------------
try:
    from gpts.meta_sync import policy_from_summary_meta  # if our earlier file exists
except Exception:
    @dataclass
    class _FallbackPolicy:
        mode: str = "balanced"
        threshold: float = 0.90
        require_evidence: bool = False
        hedging_language: bool = True
        factual_density: str = "normal"
        emotional_tone: str = "neutral"
        meta_snapshot: Dict[str, Any] | None = None
        diagnostic: str = "meta_sync not found; using defaults"
    def policy_from_summary_meta(_: Optional[Path] = None):
        return _FallbackPolicy()

try:
    # particle exporter, if present, will persist JSON particles to /particles/...
    from particle_exporter import export_particle
except Exception:
    export_particle = None

# ---- Reliability scoring (fallback mirrors earlier policy) -------------------
def _score_reliability(text: str, has_evidence: bool, true_intent_clear: bool, contradiction: bool, threshold: float) -> Dict[str, Any]:
    weights = {
        "no_emotional": 0.15, "no_speculation": 0.15, "has_evidence": 0.20,
        "clear_intent": 0.15, "length_ok": 0.10, "no_contradiction": 0.25,
    }
    penalties = {"emotional": -0.10, "missing_evidence": -0.15, "contradiction": -0.20, "true_intent_bonus": +0.10}
    score = 0.0; bonus = {}; malus = {}
    if not re.search(r"おそらく|たぶん|と思われ|感じ|hope|maybe|probably", text): score += weights["no_emotional"]; bonus["no_emotional"]=weights["no_emotional"]
    else: malus["emotional"]=penalties["emotional"]
    if not re.search(r"推測|予想|かもしれ|guess|speculat", text): score += weights["no_speculation"]; bonus["no_speculation"]=weights["no_speculation"]
    if has_evidence: score += weights["has_evidence"]; bonus["has_evidence"]=weights["has_evidence"]
    else: malus["missing_evidence"]=penalties["missing_evidence"]
    if true_intent_clear: score += (weights["clear_intent"]+penalties["true_intent_bonus"]); bonus["clear_intent"]=weights["clear_intent"]+penalties["true_intent_bonus"]
    if len(text) > 10: score += weights["length_ok"]; bonus["length_ok"]=weights["length_ok"]
    if not contradiction: score += weights["no_contradiction"]; bonus["no_contradiction"]=weights["no_contradiction"]
    else: malus["contradiction"]=penalties["contradiction"]
    score = round(max(min(score + sum(malus.values()), 1.0), 0.0), 3)
    status = "promoted" if score >= threshold else "record_only"
    return {"score": score, "status": status, "bonuses": bonus, "penalties": malus}

# ---- Intent parsing (True Intent) --------------------------------------------
def _parse_true_intent(user_text: str) -> Dict[str, str]:
    categories = [
        ("Operational Automation", r"(自動|定期|スケジュール|毎|周期)"),
        ("Evidence Integration",   r"(URL|https?://|値|データ|根拠|出典|証拠)"),
        ("Reliability Framework",  r"(信頼度|スコア|評価基準|threshold|Reliability)"),
        ("Meta Evaluation",        r"(EVAL|自己検証|meta|評価結果|再採点)"),
    ]
    for name, pat in categories:
        if re.search(pat, user_text, re.IGNORECASE):
            return {"Category": name, "Details": user_text[:240]}
    return {"Category": "General Reflection", "Details": user_text[:240]}

# ---- GPT Design class --------------------------------------------------------
@dataclass
class GPTDesign:
    threshold: float
    require_evidence: bool

    def generate(self, prompt: str, evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Gate output by reliability; demand evidence if policy says so."""
        true_intent = _parse_true_intent(prompt)
        has_evidence = evidence is not None and len(evidence) > 0
        # If policy requires evidence but none provided, mark as record_only and respond with request.
        if self.require_evidence and not has_evidence:
            reply = {
                "answer": "根拠（URLや数値データ）を提示してください。ポリシー上、根拠不在の回答は抑止されます。",
                "needed": ["evidence_url_or_numeric_data"],
            }
            evalr = _score_reliability("Requesting evidence", has_evidence=False, true_intent_clear=True, contradiction=False, threshold=self.threshold)
        else:
            # Minimal “deterministic” answer sketch (実際の生成器は別途接続)
            reply = {
                "answer": f"要点: {prompt[:120]}",
                "evidence_used": bool(has_evidence),
                "intent": true_intent["Category"],
            }
            evalr = _score_reliability(reply["answer"], has_evidence=has_evidence, true_intent_clear=True, contradiction=False, threshold=self.threshold)

        particle = {
            "Commit ID": str(uuid.uuid4()),
            "Parent Commit": "gpt_design",
            "True Intent": true_intent,
            "Reliability Score": evalr["score"],
            "Raw Text": reply["answer"],
            "Context ID": f"CTX_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "Processing Outcome": evalr["status"],
            "Evidence Sources": [] if not evidence else [evidence.get("source","user")],
            "Reviewer": "gpt-design",
            "Score History": [{"version":"DESIGN-1.0","score":evalr["score"],"timestamp":datetime.now(timezone.utc).isoformat()}],
            "Conflict Status": "pending",
        }
        return {"reply": reply, "evaluation": evalr, "particle": particle}

# ---- Runner ------------------------------------------------------------------
def main():
    policy = policy_from_summary_meta()
    logging.info(f"Policy: mode={getattr(policy,'mode','balanced')} threshold={getattr(policy,'threshold',0.90)} require_evidence={getattr(policy,'require_evidence',False)}")
    gpt = GPTDesign(threshold=getattr(policy,"threshold",0.90), require_evidence=getattr(policy,"require_evidence",False))

    # Demo 1: 根拠なし（policyが厳密なら抑止される）
    demo1 = gpt.generate("信頼度スコアの計算方針を教えて")
    # Demo 2: 根拠あり
    demo2 = gpt.generate("最新の評価手順を要約して（Reliability Framework）", evidence={"source":"meta/summary_meta.json"})

    # 可能なら粒子として保存
    saved_paths = []
    if export_particle:
        for px in (demo1["particle"], demo2["particle"]):
            p = export_particle(
                text=px["Raw Text"],
                evaluation={"score":px["Reliability Score"], "status":px["Processing Outcome"]},
                true_intent=px["True Intent"],
                evidence_sources=px["Evidence Sources"],
                parent_commit=px["Parent Commit"],
            )
            saved_paths.append(str(p))
        logging.info(f"Particles saved: {saved_paths}")
    else:
        # フォールバック: ローカルに設計プレビューを書き出し
        out = Path("gpt_design_preview.json")
        out.write_text(json.dumps({"demo1":demo1,"demo2":demo2}, ensure_ascii=False, indent=2), encoding="utf-8")
        logging.info(f"Preview saved: {out.resolve()}")

    print(json.dumps({"demo1":demo1["evaluation"], "demo2":demo2["evaluation"]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
