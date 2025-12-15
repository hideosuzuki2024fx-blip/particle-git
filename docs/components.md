# Core Components

## gpt_design.py

ハルシネーション抑止付き GPT 応答の中核ロジック。

- プロンプトから True Intent を推定する
- 信頼度スコアを計算し、promoted または record_only を判定する
- 粒子メタデータを生成し、必要に応じて particle_exporter に渡す

この経路を通らない応答は未評価の生出力とみなし、本番経路には載せないことを前提とします。

## gpts/meta_sync.py

meta/summary_meta.json からポリシーをロードするモジュール。

- threshold: 昇格に必要な最小スコア
- require_evidence: 証拠無しの回答を許可するかどうか

ポリシーが読み込めない場合でも、厳しめの固定ポリシーを適用し、
証拠の無い断定がそのまま通過しないようにします。

## particle_exporter.py

各応答を JSON 粒子として particles/YYYY/MM/AUTO_*.json に保存します。

粒子には少なくとも以下を含みます。

- evaluation: 信頼度評価結果
- true_intent: 解釈した意図
- text: 元の応答
- parent_commit: 親コミット識別子
- evidence_sources: 使用した証拠の一覧

これにより、いつどの意図でどの信頼度の応答が返されたかを追跡できます。

## meta/

ハルシネーション抑止ポリシーと評価ルールを置く領域です。

- eval_checklist.md / meta_rules.md / true_intent_glossary.md など
- summary_meta.json: 信頼度の平均やトレンドなどのスナップショット

ここがポリシーの単一の情報源になります。

## particles/

gpt_design.py などから書き出された粒子 JSON を保持する外部記憶です。
本番運用では Git の履歴ではなくデータストアとして扱う前提で .gitignore 済みです。

## summary/, integration_pipeline/, logs

- summary/: 最適化や傾向分析のサマリ
- integration_pipeline/: 粒子をまとめて評価し、ポリシーを更新するためのパイプライン
- 各種 *.log: 実行ログ（再生成可能なため Git からは除外）
