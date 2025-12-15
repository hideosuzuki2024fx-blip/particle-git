# GPT External Behavior Specification (particle-git)

このリポジトリは、GPT の振る舞い・制約・出力プロトコルを「外部仕様」として管理します。
GPT は、ここに書かれていない仕様を推測で補完してはいけません。

## Documents
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
