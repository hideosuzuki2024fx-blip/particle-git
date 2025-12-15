# Legacy README Migration Plan

対象: README.legacy.md

## 方針
- README.md は「入口」に固定し、詳細は rules/ と protocols/ と docs/ に分割する。
- 仕様（MUST/MUST NOT/CONTEXT）は rules/ に置く。
- 出力形式（コード提示、レビュー構造など）は protocols/ に置く。
- 参照URL一覧は docs/sources_for_gpt.md に集約する。

## 移行状況
- [x] 目的/ゴール → docs/overview.md
- [x] Core Components → docs/components.md
- [x] Quickstart → docs/quickstart.md
- [x] CLI → docs/cli.md
- [x] 集計パイプライン → docs/pipeline.md
- [x] Sources for GPT → docs/sources_for_gpt.md（統合）

## 次の候補（README.legacy の残りに応じて追加）
- [ ] 未収載の章があれば docs/ に新規作成して移植

## マージ後の作業
- [ ] docs/sources_for_gpt.md の main 参照を必要に応じて拡充

