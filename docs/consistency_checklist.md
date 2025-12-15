# Consistency Checklist (Personalization vs Repo Rules)

目的: パーソナライズ（1500文字）と repo 仕様（rules/・protocols/・docs/・meta/）の矛盾・重複・誤読を減らす。

## 0. 参照優先順位（短い版）
- 最小コア: docs/personalization_min_core.txt
- 詳細仕様: rules/・protocols/・docs/
- ポリシーの単一の情報源: meta/

## 1. 返答前チェック（捏造・誤断定を防ぐ）
- 不明点がある → 「不明」「この情報からは判断できません」と明示する
- 未確認のことを「見た/読んだ/確認した/アクセスした」等と言わない
- 根拠や参照元が示せない内容を断定しない
- 「絶対」「100%」などの保証表現を使わない

## 2. URL が提示された場合（web）
- web ツールが利用可能なら必ず一度アクセスを試みる
- 失敗した場合は「URL・失敗段階・エラー内容のみ」を報告し、本文を推測しない
- web ツール未実行なら「この環境からはそのURLの内容は分かりません」とだけ述べる

## 3. GitHub の参照（Raw URL）
- 新規に URL を出すときは Raw URL を使う
  - https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
- blob URL を新規に出さない

## 4. PowerShell を提示する場合（安全構造）
- Set-Location "E:\ai_dev_core" から開始する
- git rev-parse --show-toplevel で repo ルート特定 → Set-Location
- git rev-parse --is-inside-work-tree で作業ツリー確認
- Git チェックに失敗したら以降のファイル操作・git コマンドを実行しない構造にする
- 1本のスクリプトでファイル操作→git add→git commit まで完結させる（git push は含めない）
- 「手作業」「一部省略」を書かない

## 5. 長文コードの扱い（分断対策）
- 1つのコードブロックで安全に表示しきれない可能性がある場合は、
  コード本文をファイルとして生成する PowerShell を提示する
- ファイル生成 → git add → git commit まで同一スクリプトで完結させる

## 6. 変更時のチェック（repo 側）
- rules/・protocols/・docs/・meta/ のどこに置くべきかを先に決める（重複させない）
- docs/sources_for_gpt.md に相対パスを追加する（参照経路を固定）
- README.md の Documents に追記する（入口を迷わせない）
