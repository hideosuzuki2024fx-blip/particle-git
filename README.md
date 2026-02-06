# GPT External Behavior Specification (particle-git)

このリポジトリは、GPT の振る舞い・制約・出力プロトコルを「外部仕様」として管理します。
GPT は、ここに書かれていない仕様を推測で補完してはいけません。
ポリシー（評価ルール/チェックリスト/意図カテゴリ等）の単一の情報源は `meta/` です。

## Documents
- protocols/response-templates.md : 失敗時・不確実時の定型応答テンプレ
- docs/consistency_checklist.md : パーソナライズ最小コアとrepo仕様の整合チェックリスト
- docs/personalization_min_core.md : パーソナライズ（1500文字）最小コアのテンプレ
- docs/policy_layering.md : パーソナライズとrepoルールの重複削減方針
- docs/overview.md : フレームワーク概要と Goals
- docs/components.md : Core Components（役割の要約）
- docs/quickstart.md : Quickstart
- docs/cli.md : CLI（gpt_cli.py）
- docs/pipeline.md : 集計パイプライン（aggregate_particles）
- rules/core.md : 常時適用の基本制約（ハルシネーション抑制）
- rules/web.md : URLが提示された場合のWeb取得・失敗時の報告規則
- rules/github.md : GitHub関連（Raw URL優先など）
- rules/powershell.md : ローカルGit(E:\)・PowerShell提示時の安全規則
- protocols/code-output.md : コード提示時の出力プロトコル
- protocols/review.md : 現状把握→問題点→改善案の提示プロトコル
- docs/sources_for_gpt.md : GPTが参照してよいソース一覧（Raw URL）

## Structure
- `docs/`: 仕様・方針・運用ドキュメント
- `rules/`: 常時適用ルール（core/web/github/powershell）
- `protocols/`: 応答・出力プロトコル
- `meta/`: ポリシーの単一ソース（taxonomy/checklist など）
- `particles/`: 生成パーティクルデータ

## Change Log
### 2026-02-06
- `build/`, `ai_core_gpt.egg-info/`, `ai_core_gpt/__pycache__/` を削除し、Python生成物を整理。
- 実行ログ（`*.log`）のコミット済みファイルを削除。
- `.gitignore` に `build/`, `dist/`, `*.egg-info/` を追加。


