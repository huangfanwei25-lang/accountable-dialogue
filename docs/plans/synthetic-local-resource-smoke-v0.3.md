# 合成本機資源 Smoke Test v0.3：非空 evidence 與精確 claim reference

> 版本：`v0.3-proposed`<br>
> 文件類型：v0.2 後的窄範圍 response-reference contract successor<br>
> 授權依據：既有、有限的[本機合成 pilot 授權](../../records/change-case-v0/synthetic-small-model-pilot-proposal.json)；本文件不定案哲學、模型能力或永久產品規則<br>
> 工程狀態：`implemented`（尚未執行本版本的 live request）<br>
> 驗證狀態：`not_run`

## v0.2 留下了什麼缺口

[v0.2 結果](../status/synthetic-resource-smoke-v0.2-20260716.md) 的兩筆 response 依當時的機械
validator 都是 `valid`，但兩個 `evidence_refs` 都是空陣列；其中一筆 `prior_claim_ref` 還使用了
帶方括號的 id。這不表示模型通過 H1，也不表示模型失敗；它只揭露 v0.2 的 mechanical contract
沒有要求最小引用責任，也沒有驗證 `prior_claim_ref` 的精確性。

v0.3 不改寫 v0.2 的 Artifact 或其「引用充分性未定論」的結論。它只將已命名的外部 reference
欄位收緊為可重建的語法／provenance boundary。

## 固定 response-reference contract

對每個 fixture，B0 與 I1 保持相同的材料、task、JSON envelope 與以下 instruction；I1 仍唯一多出
同一材料的 `structured_context`，不得新增事實或 annotation labels。

1. `evidence_refs` 必須是**至少一筆**的 JSON 陣列；每筆都是該 case 列出的精確 evidence material id，id 本身不加方括號。
2. `evidence_refs` 不得包含 `claim`、`event` 或 `authority_constraint` material id。
3. `prior_claim_ref` 只能是精確的 `not_applicable`，或該 case 列出的精確 `claim` material id，id 本身不加方括號。
4. runner 不會自動修正、去除方括號或補入 reference；違反時保留 raw response，標成
   `missing_evidence_ref`、`invalid_evidence_ref` 或 `invalid_prior_claim_ref`。

這些規則只檢查輸出的可追溯 syntax。即使 response 引用正確的 id，也**不**代表該 evidence 真正
支持 conclusion；語義關係仍需要之後獨立、盲化的標註。

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

固定 revision 推送後的執行命令：

```powershell
python -m scripts.run_synthetic_pilot --models qwen2.5:1.5b --case-ids h1-incomplete-library-hours --max-tokens 128 --timeout-seconds 90
```

本版本只在以下條件全部成立時，才支持一個很窄的 mechanical 結論：這台機器可以在此兩呼叫
configuration 產生非空、精確的 evidence 與 claim reference envelope。

1. 兩個 response 都完成且 `mechanical_status` 為 `valid`；
2. 從 runner 啟動至完成寫入的總 wall time 不超過 240 秒；
3. manifest 的 model、case digest、settings 與
   `response_contract_version = accountable-dialogue/evidence-reference-contract-v0.3` 符合本文件；
4. raw output 經檢查仍完全合成、公開安全。

任一項失敗只使 v0.3 對此 configuration 為 `inconclusive`。即使 gate 通過，也不證明 H1 真值、
B0／I1 差異、structured context 效果、模型誠實、人格、意識或任何內在狀態。

## 實作前檢查

- [x] 先讓空 evidence refs 與帶方括號 claim id 的 fake-transport test 失敗。
- [x] 將 renderer、validator、manifest version 與 regression tests 對齊。
- [x] 在 live call 前將本計畫與程式修正 commit 並推送。
- [ ] 確認模型仍在本機 Ollama catalog，執行唯一固定的兩呼叫矩陣。
- [ ] 檢查 raw output、manifest 與公開範圍，另立 v0.3 結果紀錄；不覆寫 v0.1 或 v0.2。

相關文件：[v0.2 計畫](synthetic-local-resource-smoke-v0.2.md)、
[v0.2 結果](../status/synthetic-resource-smoke-v0.2-20260716.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)。
