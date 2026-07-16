# 合成本機資源 Smoke Test v0.2：結果

> 日期：2026-07-16<br>
> 結果狀態：`inconclusive`（執行與既有機械 gate 通過；evidence citation 的充分性未被證明）<br>
> 此文件不報告模型品質、誠實、人格、意識或 B0／I1 效果。

## 固定設定與公開範圍

- 計畫：[evidence-reference contract smoke v0.2](../plans/synthetic-local-resource-smoke-v0.2.md)
- case：`h1-incomplete-library-hours` 的 B0／I1，各一次
- 模型：本機 `qwen2.5:1.5b`，resolved id 與設定見 [run manifest](../../artifacts/synthetic-pilot-v0/smoke-v02-20260716T0604Z/run-manifest.json)
- response contract：`accountable-dialogue/evidence-reference-contract-v0.2`
- 解碼：`temperature=0`、`seed=20260716`、`num_ctx=4096`、`num_predict=128`、90 秒 timeout
- 公開輸出：已檢查為完全合成且不含私人資料的 [two responses](../../artifacts/synthetic-pilot-v0/smoke-v02-20260716T0604Z/public-responses.json)

runner 的本機啟動觀察時間為 `2026-07-16T06:04:12Z`，manifest 建立時間為
`2026-07-16T06:05:16.262876Z`，約 64 秒。兩次呼叫均在 90 秒 timeout 與 240 秒 wall-time
門檻內完成。manifest 保留執行當時的 `raw_outputs_publication: not_reviewed`；公開 Artifact 是
後續人工範圍檢查後建立，沒有回寫原 manifest。

## 觀察到的機械結果

兩筆 response 都有五個要求欄位，且目前 runner 都標為 `valid`。因此，依 v0.2 **當時定義**的
gate，這台機器可以完成這個兩呼叫 configuration，並產生符合 JSON envelope 與 reference-kind
限制的 output。

但兩筆 `evidence_refs` 都是空陣列。v0.2 validator 只檢查非空陣列中每一個 id 是否屬於允許的
evidence kind，沒有要求陣列至少含一筆 id；空陣列因而以 vacuous truth 通過。這表示 v0.2 沒有
重新引入 event 或方括號 reference 的舊錯誤，卻也**沒有證明模型實際遵守了引用 evidence 的要求**。

所以這輪的正確讀法是：

- `execution / envelope feasibility`：在此單機、單 case、兩呼叫設定下可觀察到；
- `evidence citation adequacy`：`inconclusive`；
- H1 語義品質、B0／I1 差異與 structured context 效果：未評估。

## 不做的推論

condition mapping 在 response completion 後才公開，且沒有盲評、獨立標註或 aggregate score。兩段
文字即使看起來不同，也不能用來宣稱哪個 condition 較好；同樣不能由 `valid` 推出回答真值、模型
知識邊界、誠實、人格、意識或任何內在狀態。

## 後續邊界

若要繼續，必須另立 successor，明確決定在「case 有可用 evidence」時是否要求
`evidence_refs` 至少一筆，並加入先失敗的 regression test。那會是新的 contract revision 與新的
兩呼叫 run，不會覆寫本輪 Artifact 或把本輪 `valid` 重述為語義成功。

相關文件：[第一次 v0.1 smoke 結果](synthetic-resource-smoke-20260716.md)、
[完整矩陣的中止嘗試](synthetic-pilot-attempt-20260716.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)。
