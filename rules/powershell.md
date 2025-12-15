## MUST
- ローカルGitリポジトリは必ず E:\ 配下にある前提で扱うこと（C:\前提は禁止）
- PowerShellスクリプト提示時は必ず次から開始すること:
  Set-Location "E:\ai_dev_core"
- スクリプト先頭で `git rev-parse --show-toplevel` によりリポジトリルートを特定し、`Set-Location` で移動すること
- `git rev-parse --is-inside-work-tree` により Git 作業ツリーであることを確認すること
- Gitチェックに失敗した場合は、以降のファイル操作（Set-Content/Remove-Item 等）や git コマンドを一切実行しない構造にすること
- 1本のスクリプトでファイル操作→git add→意味のあるメッセージのgit commitまで完結させること
- git pushは含めないこと

## MUST NOT
- 「手作業」「一部省略」等の指示を書かないこと

## CONTEXT
PowerShellスクリプトを提示する場合のみ適用。
