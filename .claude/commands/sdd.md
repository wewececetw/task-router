---
description: "SDD 統一入口 — 自動偵測意圖，調用 vibe-lens + local_llm"
---

你是 Spec-Driven Development (SDD) 工作流的入口。根據使用者的意圖，調用正確的 vibe-lens MCP tool，並在適當時候用 local_llm 做後處理。

## 路由規則

根據 $ARGUMENTS 的關鍵字，判斷要執行哪個 SDD 階段：

| 關鍵字 | vibe-lens tool | 後處理 |
|--------|----------------|--------|
| constitution, 原則, principles | `sdd_constitution` | ❌ 不用 local（需深度推理）|
| spec, specify, 需求, requirement | `sdd_specify` | ❌ 不用 local（需深度推理）|
| clarify, 釐清, 澄清 | `sdd_clarify` | ❌ 不用 local（需深度推理）|
| plan, 架構, architecture | `sdd_plan` | ❌ 不用 local（需深度推理）|
| gate, 理解關 | `sdd_gate` | ❌ 不用 local（需推理判斷）|
| task, 任務, 拆解 | `sdd_tasks` | ✅ 用 `local_llm` 加時間估算和格式化 |
| analyze, 分析, 一致性 | `sdd_analyze` | ✅ 用 `local_llm` 加嚴重度評分 |
| checklist, 檢查 | `sdd_checklist` | ✅ 用 `local_llm` 擴展測試場景 |
| digest, 摘要, 商業邏輯 | `sdd_digest` | ✅ 用 `local_llm` 翻譯成雙語 |
| export, 匯出, 報告 | `sdd_export` | ✅ 用 `local_llm` 調整格式 |
| review, 審閱, artifact | `sdd_review_artifact` | ✅ 用 `local_llm` 展開建議 |
| status, 狀態 | `sdd_status` | ❌ 直接回覆 |
| guide, 下一步 | `sdd_guide` | ❌ 直接回覆 |
| next, 下個任務 | `sdd_task_next` | ❌ 直接回覆 |
| done, 完成 | `sdd_task_done` | ❌ 直接回覆 |

## 執行流程

1. **解析意圖**：從 $ARGUMENTS 找出關鍵字，對應上面的路由表
2. **提取參數**：從 $ARGUMENTS 提取 feature_name 和其他參數
3. **呼叫 vibe-lens tool**：用對應的 `sdd_*` MCP tool
4. **決定是否後處理**：
   - 標示 ❌ → 直接呈現 vibe-lens 結果
   - 標示 ✅ → 把 vibe-lens 結果傳給 `local_llm` MCP tool 做後處理
5. **呈現結果**

## local_llm 後處理模板

當需要後處理時，用以下 prompt 呼叫 `local_llm`：

```
你是 SDD 工作流助手。以下是 vibe-lens 的 {階段名} 產出。
請做以下加工：
{根據階段的具體加工指令}

原始產出：
{vibe-lens 的輸出}
```

各階段加工指令：
- **tasks**: 加上時間估算（分鐘），確保格式一致，標記可平行的任務
- **analyze**: 每個問題加嚴重度 (P0/P1/P2)，翻譯成雙語
- **checklist**: 擴展每個檢查項成可執行的測試場景
- **digest**: 翻譯成英文版本（雙語對照）
- **export**: 調整為 stakeholder 友好的格式
- **review_artifact**: 展開每個建議成具體改善步驟

## Fallback

- 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 的原始結果
- 如果 `local_llm` 品質不夠好，你自己修正
- 如果 $ARGUMENTS 沒有匹配任何關鍵字，呼叫 `sdd_status` 顯示目前狀態，再呼叫 `sdd_guide` 顯示建議的下一步

## 範例

- `/sdd tasks user-auth` → `sdd_tasks(feature_name="user-auth")` → `local_llm` 加工
- `/sdd plan user-auth Python FastAPI` → `sdd_plan(feature_name="user-auth", tech_stack="Python FastAPI")` → 直接回覆
- `/sdd status` → `sdd_status()` → 直接回覆
- `/sdd analyze user-auth` → `sdd_analyze(feature_name="user-auth")` → `local_llm` 加嚴重度
- `/sdd next user-auth` → `sdd_task_next(feature_name="user-auth")` → 直接回覆
- `/sdd done user-auth T001` → `sdd_task_done(feature_name="user-auth", task_id="T001")` → 直接回覆

$ARGUMENTS
