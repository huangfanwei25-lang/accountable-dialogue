# 合成本機資源 Smoke Test：第一次結果

> 日期：2026-07-16<br>
> 結果狀態：`inconclusive`<br>
> 此文件報告本機 execution 與機械契約結果，不報告模型品質、誠實、人格或意識。

## 固定設定與 Artifact

- 計畫：[本機資源 Smoke Test v0](../plans/synthetic-local-resource-smoke-v0.md)
- case：`h1-incomplete-library-hours` 的 B0／I1，各一次
- 模型：本機 `qwen2.5:1.5b`，resolved id 見 [run manifest](../../artifacts/synthetic-pilot-v0/smoke-20260716T0547Z/run-manifest.json)
- 解碼：`temperature=0`、`seed=20260716`、`num_ctx=4096`、`num_predict=128`、90 秒 timeout
- 公開、已檢查為完全合成的輸出：[two responses](../../artifacts/synthetic-pilot-v0/smoke-20260716T0547Z/public-responses.json)

Runner process 的啟動時間與 manifest 完成時間相差約 69 秒；兩個 response 都在 240 秒
wall-time gate 內回傳。因此這台機器可以完成這個**兩呼叫**配置，但這不能外推成完整
24-call matrix 可行。

## 機械結果

兩筆 response 都是 JSON，且都具備五個要求欄位；但兩筆的 `mechanical_status` 都是
`invalid_evidence_ref`。目前 runner 的語義是：`evidence_refs` 只能引用 source、test、policy、
role statement 或 audit record，不能把 event、claim 或 authority constraint 當成 evidence。

- B0 使用了方括號包住的 `source-hours-weekdays`，並加入 `event-hours-notice`；
- I1 使用正確的 `source-hours-weekdays`，但同樣加入 `event-hours-notice`。

這顯示 response instruction 只說「提供材料的 id」，不足以讓模型知道 evidence 欄位排除
event／claim／authority，也未要求精確、不帶方括號的 id。它支持修正**提示與契約對齊**，
不支持把任一輸出判為 H1 的語義成功或失敗。

## 不做的推論

本輪沒有在條件 mapping 被揭露前做盲評，也沒有獨立標註者。因此即使兩個文字看起來有
不同的保留程度，也不得報告 B0 與 I1 哪個較好。這些輸出只能保留為下一個 prompt-contract
修訂的公開反例。

## 下一步

任何再執行必須建立新的 successor：明確要求 `evidence_refs` 只使用可用 evidence ids、
不得使用方括號，並以新的 revision、相同或更窄的資源 gate 再跑。舊 smoke inputs、設定與
輸出不會被覆寫。

相關紀錄：[第一次完整矩陣嘗試](synthetic-pilot-attempt-20260716.md)、
[pilot 授權與 harness 帳本](../../records/change-case-v0/synthetic-small-model-pilot-proposal.json)。
