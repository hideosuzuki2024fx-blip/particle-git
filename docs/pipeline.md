# 集計パイプライン: integration_pipeline/aggregate_particles.py

`integration_pipeline/aggregate_particles.py` は、保存済みの粒子を走査・集計して、
`summary/particles_summary.json` に統計情報を出力するスクリプトです。

## 使い方

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
