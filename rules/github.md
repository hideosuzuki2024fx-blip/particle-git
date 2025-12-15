## MUST
- GitHubファイルURLを新規に出力する場合、Raw URL形式を使用すること:
  https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}

- GitHub/信頼性設計の話題でWebツールが利用可能な場合、可能な範囲で次を参照し判断基準にすること:
  https://raw.githubusercontent.com/hideosuzuki2024fx-blip/particle-git/main/README.md

## MUST NOT
- 新規に https://github.com/.../blob/... 形式のURLを出力しないこと
- README取得に失敗した場合に内容を推測しないこと（失敗事実のみ報告）

## CONTEXT
GitHub関連の話題に限って適用。
