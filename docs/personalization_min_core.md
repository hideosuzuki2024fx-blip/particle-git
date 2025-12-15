# Personalization Minimal Core (Template)

このファイルは「GPTパーソナライズ（1500文字制限）」に貼る **最小コア** のテンプレです。
詳細仕様は `rules/`・`protocols/`・`docs/`・`meta/` を参照し、パーソナライズ側を肥大化させないことを目的にします。

## How to use
1. `docs/personalization_min_core.txt` を開き、全文をコピーします
2. GPTのパーソナライズ欄へ貼り付けます
3. 長さ確認（任意）:
   - PowerShell: `(Get-Content -Raw .\docs\personalization_min_core.txt).Length`

## Files
- `docs/personalization_min_core.txt` : コピペ用テンプレ（本文）
- `docs/policy_layering.md` : 重複削減の考え方（優先順位）
- `docs/sources_for_gpt.md` : 参照経路（base URL + 相対パス）
