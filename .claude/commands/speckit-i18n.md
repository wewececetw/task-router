---
description: "用本地模型翻譯 i18n 字串檔"
---

**請使用 local_llm MCP tool** 翻譯 i18n 字串。

步驟：
1. 讀取來源語言的 i18n 檔案（如 `en.json`）
2. 用 `local_llm` tool 翻譯，prompt：

```
將以下 i18n JSON 翻譯成 {目標語言}。
規則：
- 保持 key 不變，只翻譯 value
- 保留 {{variable}} 和 {0} 等佔位符
- 保持 JSON 格式
- 用詞自然口語化

{i18n JSON 內容}
```

3. 寫入對應的語言檔案

$ARGUMENTS
