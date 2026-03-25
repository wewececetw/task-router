---
description: "用本地模型從 git diff 生成 changelog"
---

**請使用 local_llm MCP tool** 生成 changelog。

步驟：
1. 執行 `git log --oneline -20` 和 `git diff HEAD~5` 取得最近的變更
2. 用 `local_llm` tool 生成 changelog，prompt：

```
根據以下 git log 和 diff，生成 CHANGELOG 條目。
格式：Keep a Changelog (https://keepachangelog.com/)

分類：
### Added - 新功能
### Changed - 既有功能的變更
### Fixed - 修復
### Removed - 移除

Git log:
{git log}

Diff summary:
{git diff --stat}
```

3. 將結果插入 `CHANGELOG.md` 頂部（或建立新檔）

$ARGUMENTS
