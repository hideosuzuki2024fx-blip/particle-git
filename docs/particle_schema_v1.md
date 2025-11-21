# Particle Schema V1

`particle_exporter.py` が出力する粒子 JSON のスキーマ定義です。

## Top-level Fields

- `Commit ID` (string)  
  - 形式: `AUTO_YYYYMMDD_HHMMSS_xxxxxx`
  - 粒子の一意なID。ファイル名（拡張子なし）と一致。

- `Parent Commit` (string)  
  - この粒子を生成した設計やランタイムの識別子。例: `DESIGN_V1.0_002`, `gpt_design`

- `True Intent` (object)
  - `Category` (string): 意図の分類。例: `Reliability Framework`, `Operational Automation`
  - `Details` (string): ユーザー入力に対する意図の短い説明。

- `Reliability Score` (number)
  - 0.0〜1.0 の信頼度スコア。
  - threshold (例: 0.9) 以上であれば `promoted` 候補。

- `Raw Text` (string)
  - 実際に生成された応答のテキスト。

- `Context ID` (string)
  - 文脈やバッチ処理単位のID。形式の一例: `CTX_YYYYMMDDHHMMSS`

- `Processing Outcome` (string)
  - 粒子の扱い。現時点の主な値:
    - `promoted` : 表に出す候補として採用
    - `record_only` : 記録のみ（外部には出さない）

- `Evidence Sources` (array)
  - 使用した証拠の識別子リスト。例: `["meta/summary_meta.json"]` など。
  - 証拠が無い場合は空配列。

- `Reviewer` (string)
  - 粒子を生成したロジック／エージェント名。例: `gpt-design`, `gpt-design (migrated)`

- `Score History` (array of object)
  - スコアの変遷。
  - 各要素:
    - `version` (string): 評価バージョン。例: `DESIGN-1.1`, `DESIGN-1.1-migrated`
    - `score` (number): 当該バージョンでのスコア
    - `timestamp` (string): ISO 8601 形式のタイムスタンプ

- `Conflict Status` (string)
  - 粒子間の矛盾や再評価の状態。初期値は `pending`。

## Notes

- すべての粒子は、この V1 スキーマに揃える。
- 将来スキーマを変更する場合は、ここに V2+ の定義を追加し、
  マイグレーションスクリプトを `tools/` 等に配置する。
