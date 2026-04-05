---
description: "用本地模型從 git diff 生成 changelog"
---

從 git 歷史生成 changelog。

步驟：
1. 用 Bash 取得 git 變更：`git log --oneline -20 && git diff --stat HEAD~5`
2. 用 Bash 執行 `./scripts/call-omlx.sh` 生成 changelog：

```bash
./scripts/call-omlx.sh "根據以下 git log 和 diff，生成 CHANGELOG 條目。
格式：Keep a Changelog (https://keepachangelog.com/)

分類：
### Added - 新功能
### Changed - 既有功能的變更
### Fixed - 修復
### Removed - 移除

Git log:
{git log}

Diff stat:
{git diff --stat}" --max-tokens 2048 --temperature 0.5
```

3. 將結果用 Write 插入 `CHANGELOG.md` 頂部（或建立新檔）
4. 如果 FALLBACK，你自己寫 changelog

$ARGUMENTS
