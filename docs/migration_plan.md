# Legacy README Migration Plan

対象: README.legacy.md

## 方針
- README.md は「入口」に固定し、詳細は rules/ と protocols/ と docs/ に分割する。
- 仕様（MUST/MUST NOT/CONTEXT）は rules/ に置く。
- 出力形式（コード提示、レビュー構造など）は protocols/ に置く。
- 参照URL一覧は docs/sources_for_gpt.md に集約する。

## まず移す候補（チェックして埋める）
- [ ] 目的/ゴール → docs/overview.md
- [ ] 判断基準/スコア/判定ルール → rules/（新規ファイル or 既存へ追記）
- [ ] CLI/運用フロー → docs/operations.md
- [ ] 参照すべき Raw URL 一覧 → docs/sources_for_gpt.md（追記・整理）
