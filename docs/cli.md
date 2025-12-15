# CLI: gpt_cli.py

`gpt_cli.py` は、コマンドラインから GPTDesign を 1 回呼び出し、
ポリシーに従って応答をゲートしたうえで粒子を書き出す CLI です。
結果は JSON 形式で標準出力に返されます。

## 使い方

- 証拠なしで実行する場合（`require_evidence = true` のときは原則 record_only 扱い）:

```bash
python gpt_cli.py "信頼度スコアの計算方針を教えて"
```

- 証拠ありで実行する場合（例: `meta/summary_meta.json` を根拠としてマーク）:

```bash
python gpt_cli.py "最新の評価手順を要約して（Reliability Framework）" --evidence-source meta/summary_meta.json
```

出力 JSON には少なくとも次が含まれます。

- `answer` : 実際に返された文面と、証拠を使ったかどうか
- `evaluation` : score / status / bonuses / penalties
- `true_intent` : Category / Details
- `particle_meta` :
  - `internal_commit_uuid` : GPTDesign 内部で採番した UUID
  - `storage_commit_id` : 粒子ファイル名の stem（`AUTO_...`、V1 `"Commit ID"` と一致）
  - `processing_outcome` : `promoted` / `record_only`
  - `saved_path` : `particles/YYYY/MM/AUTO_*.json` へのパス

`require_evidence = true` かつ証拠が渡されない場合、
応答は「根拠の提示を求める」メッセージとなり、粒子は `record_only` として保存されます。
