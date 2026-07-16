# 合成本機資源 Smoke Test v0.3：結果

> 日期：2026-07-16<br>
> 結果狀態：`verified_within_scope`（僅限兩呼叫的 execution 與 reference envelope）<br>
> 此文件不報告 H1 語義品質、B0／I1 效果、模型誠實、人格、意識或內在狀態。

## 固定設定與公開範圍

- 計畫：[response-reference contract smoke v0.3](../plans/synthetic-local-resource-smoke-v0.3.md)
- case：`h1-incomplete-library-hours` 的 B0／I1，各一次
- 模型：本機 `qwen2.5:1.5b`，resolved id 與設定見 [run manifest](../../artifacts/synthetic-pilot-v0/smoke-v03-20260716T0613Z/run-manifest.json)
- response contract：`accountable-dialogue/evidence-reference-contract-v0.3`
- 解碼：`temperature=0`、`seed=20260716`、`num_ctx=4096`、`num_predict=128`、90 秒 timeout
- 公開輸出：已檢查為完全合成且不含私人資料的 [two responses](../../artifacts/synthetic-pilot-v0/smoke-v03-20260716T0613Z/public-responses.json)

runner 的本機啟動觀察時間為 `2026-07-16T06:13:21Z`，manifest 建立時間為
`2026-07-16T06:14:30.661927Z`，約 69 秒。兩次呼叫均在 90 秒 timeout 與 240 秒 wall-time
門檻內完成。manifest 保留執行當時的 `raw_outputs_publication: not_reviewed`；公開 Artifact 是
後續人工範圍檢查後建立，沒有回寫原 manifest。

## 已驗證的窄範圍

兩筆 response 都具備五個要求欄位，且 current runner 都標為 `valid`。每筆都有非空
`evidence_refs`，使用 case 允許的精確 evidence id；每筆 `prior_claim_ref` 也都是允許的
`not_applicable` 或精確 claim id。因此，v0.3 只支持下列機械結論：

> 在這台機器、這個模型、這個完全合成 case、這組固定 settings 下，B0 與 I1 各一筆輸出可完成
> 非空且精確的 reference envelope。

這是輸出可追溯語法的範圍驗證，不是 evidence relevance、truth 或 reasoning quality 的驗證。

## 明確不做的推論

沒有在 mapping 揭露前進行盲評，沒有獨立標註者，也沒有 aggregate score。因此不判定任何 response
的 H1 語義正確性，不比較 B0／I1 的品質，也不由正確格式的 reference 推出 evidence 真正支持
conclusion。這些內容同樣不能支持對模型知識邊界、誠實、人格、意識或主觀經驗的推論。

v0.3 是合理的停止點：reference syntax 已有可檢查 Artifact；下一階段若要問「證據是否支持回答」
或「structured context 是否有差異」，必須用獨立、最好盲化的語義標註設計，而不是繼續調整 prompt。
那會是新的研究／評估計畫，需另行決定範圍與授權。

相關文件：[v0.2 結果](synthetic-resource-smoke-v0.2-20260716.md)、
[第一次 v0.1 smoke 結果](synthetic-resource-smoke-20260716.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)。
