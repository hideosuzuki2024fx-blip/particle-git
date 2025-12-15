# Sources for GPT (Raw URLs)

この一覧は、GPT が参照してよい「外部仕様ソース」です。
**Raw URL の base（ref）+ 相対パス**で管理します。

## Base URL（ref）
- マージ前（PR確認中）: https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/chore/external-spec-structure/
- マージ後（main）    : https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/

> 以降に列挙するパスは、上記 base の末尾に連結して使います。

## Entry
- README.md

## External behavior spec
- rules/core.md
- rules/web.md
- rules/github.md
- rules/powershell.md
- protocols/code-output.md
- protocols/review.md

## Docs (split from legacy README)
- docs/overview.md
- docs/components.md
- docs/quickstart.md
- docs/cli.md
- docs/pipeline.md
- docs/migration_plan.md
- docs/personalization_min_core.md
- docs/personalization_min_core.txt
- docs/consistency_checklist.md

## Policy / Meta rules (single source of truth)
- meta/meta_rules.md
- meta/eval_checklist.md
- meta/true_intent_glossary.md
- meta/summary_meta.json

## Core design / CLI
- gpt_design.py
- gpt_cli.py
- gpts/meta_sync.py
- particle_exporter.py

## Integration
- integration_pipeline/aggregate_particles.py
- integration_pipeline/optimizer.py

## Example
- (PR ref) README.md:
  https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/chore/external-spec-structure/README.md
- (main) README.md:
  https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/README.md


