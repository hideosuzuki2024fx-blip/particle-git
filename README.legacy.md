# AI Core GPT – Hallucination-Resistant Reliability Framework

particle-git は、GPT の出力をそのまま通さずに

- 信頼度スコアでゲートし、
- 各応答を「粒子（particle）」として外部記憶に保存し、
- 後から再評価・統合できるようにする

ためのフレームワークです。

このリポジトリは、ハルシネーションを前提に言い訳させるためではなく、
ハルシネーションを抑止するための制御レイヤーとして設計されています。

## Goals

- 根拠のない断定を事前にブロックする
- 各応答を粒度の細かい particle commit として記録し、後から検証できるようにする
- 閾値、証拠必須フラグ、トーンなどのポリシーを外部メタデータから切り替える
- Python パッケージとスクリプトとして他のクライアントから共通利用できるようにする

## Core Components

### gpt_design.py

ハルシネーション抑止付き GPT 応答の中核ロジック。

- プロンプトから True Intent を推定する
- 信頼度スコアを計算し、promoted または record_only を判定する
- 粒子メタデータを生成し、必要に応じて particle_exporter に渡す

この経路を通らない応答は未評価の生出力とみなし、本番経路には載せないことを前提とします。

### gpts/meta_sync.py

meta/summary_meta.json からポリシーをロードするモジュール。

- threshold: 昇格に必要な最小スコア
- require_evidence: 証拠無しの回答を許可するかどうか

ポリシーが読み込めない場合でも、厳しめの固定ポリシーを適用し、
証拠の無い断定がそのまま通過しないようにします。

### particle_exporter.py

各応答を JSON 粒子として particles/YYYY/MM/AUTO_*.json に保存します。

粒子には少なくとも以下を含みます。

- evaluation: 信頼度評価結果
- true_intent: 解釈した意図
- text: 元の応答
- parent_commit: 親コミット識別子
- evidence_sources: 使用した証拠の一覧

これにより、いつどの意図でどの信頼度の応答が返されたかを追跡できます。

### meta/

ハルシネーション抑止ポリシーと評価ルールを置く領域です。

- eval_checklist.md / meta_rules.md / true_intent_glossary.md など
- summary_meta.json: 信頼度の平均やトレンドなどのスナップショット

ここがポリシーの単一の情報源になります。

### particles/

gpt_design.py などから書き出された粒子 JSON を保持する外部記憶です。
本番運用では Git の履歴ではなくデータストアとして扱う前提で .gitignore 済みです。

### summary/, integration_pipeline/, logs

- summary/: 最適化や傾向分析のサマリ
- integration_pipeline/: 粒子をまとめて評価し、ポリシーを更新するためのパイプライン
- 各種 *.log: 実行ログ（再生成可能なため Git からは除外）

## Quickstart

1. 仮想環境を作成して有効化します。
2. `pip install -r requirements.txt` を実行して依存関係を導入します。
3. `python gpt_design.py` を実行します。
4. `gpt_design_preview.json` と `particles/YYYY/MM/AUTO_*.json` を開き、
   True Intent、Reliability Score、Processing Outcome が期待どおりに付与されているかを確認します。

---

## CLI: gpt_cli.py

`gpt_cli.py` は、コマンドラインから GPTDesign を 1 回呼び出し、
ポリシーに従って応答をゲートしたうえで粒子を書き出す CLI です。
結果は JSON 形式で標準出力に返されます。

### 使い方

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

## 集計パイプライン: integration_pipeline/aggregate_particles.py

`integration_pipeline/aggregate_particles.py` は、保存済みの粒子を走査・集計して、
`summary/particles_summary.json` に統計情報を出力するスクリプトです。

### 使い方

```bash
python integration_pipeline/aggregate_particles.py
```

実行すると、少なくとも次の情報を含む JSON が生成されます。

- `generated_at` : 集計を実行した日時
- `total_particles` : 対象となった粒子の総数
- `status_counts` : `promoted` / `record_only` 等のステータス別件数
- `intents` : Intent Category ごとの統計
  - `count` : 粒子件数
  - `avg_score` : 平均スコア
  - `promoted` : promoted 件数
  - `record_only` : record_only 件数

`summary/` 配下は `.gitignore` 済みであり、
いつでも再生成可能な解析結果として扱います。

## Sources for GPT (Raw URLs)

GPT がこのリポジトリのポリシー・設計・スキーマを参照するための Raw URL 一覧です。
チャットから README の Raw URL が渡された場合、ここに列挙された URL を辿って内容を読み込むことを想定しています。

- README (this file)
  - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/README.md

- Policy / Meta rules
  - meta/meta_rules.md  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/meta/meta_rules.md
  - meta/eval_checklist.md  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/meta/eval_checklist.md
  - meta/true_intent_glossary.md  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/meta/true_intent_glossary.md
  - meta/summary_meta.json  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/meta/summary_meta.json

- Core design / CLI
  - gpt_design.py  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/gpt_design.py
  - gpt_cli.py  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/gpt_cli.py
  - gpts/meta_sync.py  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/gpts/meta_sync.py
  - particle_exporter.py  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/particle_exporter.py

- Particle schema / integration
  - docs/particle_schema_v1.md  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/docs/particle_schema_v1.md
  - integration_pipeline/aggregate_particles.py  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/integration_pipeline/aggregate_particles.py
  - integration_pipeline/optimizer.py  
    - https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/integration_pipeline/optimizer.py

