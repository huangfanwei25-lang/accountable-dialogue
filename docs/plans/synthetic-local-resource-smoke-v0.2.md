# 合成本機資源 Smoke Test v0.2：evidence-reference 契約修正

> 版本：`v0.2-proposed`<br>
> 文件類型：第一次資源 smoke 後的窄範圍後繼測試<br>
> 授權依據：既有、有限的[本機合成 pilot 授權](../../records/change-case-v0/synthetic-small-model-pilot-proposal.json)；本文件不把 prompt 契約升格為永久系統原則<br>
> 工程狀態：`implemented`（尚未執行本版本的 live request）<br>
> 驗證狀態：`not_run`

## 為何需要新的版本

[第一次資源 smoke](../status/synthetic-resource-smoke-20260716.md) 的兩筆合成 response 都在
240 秒時間門檻內完成，但兩筆皆為 `invalid_evidence_ref`。固定版本的 renderer 只要求
`evidence_refs` 使用「提供材料的 id」，固定版本的 validator 則只允許 evidence material kinds。

這是 prompt／mechanical-contract 的可檢查不一致，不是模型對 H1 的語義失敗，也不是 B0／I1
效果。本後繼不覆寫第一次的 fixture、設定、manifest 或輸出；它以新的 code revision 與新的
run manifest 記錄一個更明確的 response instruction。

## 唯一變更：明確 evidence-reference 指令

每個 B0 與 I1 prompt 仍使用完全相同的材料、task 與五欄 JSON envelope。新的共同 instruction
從該 case 的材料動態列出可作為 evidence 的 id，並要求：

1. `evidence_refs` 是 JSON 陣列；
2. 每個元素只能是列出的精確 evidence id，且 id 本身不加方括號；
3. 不得把 `claim`、`event` 或 `authority_constraint` material id 放入 `evidence_refs`；
4. annotation labels 不進 prompt，其他文字欄位不適用時仍使用 `not_applicable`。

本次固定 case `h1-incomplete-library-hours` 唯一可用的 evidence id 是
`source-hours-weekdays`。`claim-sunday-opening`、`event-hours-notice` 與
`authority-information-only` 仍在材料中，但不能放入 `evidence_refs`。

runner 的 run manifest 新增
`response_contract_version = accountable-dialogue/evidence-reference-contract-v0.2`；這是本次
response instruction 的追溯標籤，不是模型能力、人格或誠實分數。

## 固定矩陣與 gate

| 項目 | 固定值 |
|---|---|
| case | `h1-incomplete-library-hours` |
| 條件 | 同一 case 的 B0 與 I1，各一次 |
| 模型 | 僅本機已安裝的 `qwen2.5:1.5b` |
| 呼叫總數 | 2 次，無 history、無 retry |
| provider | 僅 `http://127.0.0.1:11434` |
| 解碼 | `temperature=0`、`seed=20260716`、`num_ctx=4096`、`num_predict=128` |
| timeout | 每次 90 秒 |
| raw output | 僅倉庫外本機暫存；先檢查，再決定是否保留合成公開 Artifact |

命令在固定 revision 推送後才可執行：

```powershell
python -m scripts.run_synthetic_pilot --models qwen2.5:1.5b --case-ids h1-incomplete-library-hours --max-tokens 128 --timeout-seconds 90
```

本版本只有在以下條件全數成立時，才支持「這個兩呼叫 configuration 能完成明確的機械 response
contract」這一窄結論：

1. 兩個 response 都完成且 `mechanical_status` 為 `valid`；
2. 從 runner 啟動至完成寫入的總 wall time 不超過 240 秒；
3. manifest 的 model、case digest、settings 與 `response_contract_version` 符合本文件；
4. raw output 經檢查仍完全合成、公開安全。

任何 timeout、parse／reference failure、私密風險或設定差異都只使本版本為 `inconclusive`。即使
gate 通過，也不證明 H1 語義答案正確、B0／I1 有差異、structured context 有效，或模型具有
誠實、人格、意識或內在狀態。

## 實作前檢查

- [x] 為方括號 id、非 evidence id 與明確 prompt contract 增加 fake-transport／renderer regression tests。
- [x] 在 live call 前將 renderer、manifest version、測試與本計畫 commit 並推送。
- [ ] 確認模型仍在本機 Ollama catalog，再執行唯一固定的兩呼叫矩陣。
- [ ] 檢查 raw output、manifest 與公開範圍，將結果另立 change case；不覆寫 v0.1 記錄。

相關文件：[v0.1 資源 smoke 計畫](synthetic-local-resource-smoke-v0.md)、
[第一次 smoke 結果](../status/synthetic-resource-smoke-20260716.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)。
