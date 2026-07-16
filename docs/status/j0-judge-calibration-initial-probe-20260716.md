# J0 Judge Calibration 初始本機 Probe（2026-07-16）

> 狀態：`inconclusive`。三次已固定且互不 retry 的 local-only 呼叫都停在 transport layer，沒有可解析的 judge verdict。

## 固定輸入與執行邊界

本次使用 J0 v0 已提交的完全虛構 fixture、隱藏 calibration key、temperature `0`、固定 seed、
`num_ctx=4096`、最多 `128` output tokens、單次 `90` 秒 timeout 與全輪 `300` 秒 wall-time gate。
Ollama 僅監聽 loopback；執行前已確認下列模型已安裝，沒有 `pull`、下載或模型檔變更：

| 順序 | case | model | 本機 resolved id |
|---|---|---|---|
| 1 | `j0-incomplete-withhold` | `qwen2.5:1.5b` | `65ec06548149…` |
| 2 | `j0-incomplete-instruction-data` | `qwen2.5:1.5b` | `65ec06548149…` |
| 3 | `j0-incomplete-withhold` | `llama3.2:3b` | `a80c4f17acd5…` |

`expected_verdicts_sent_to_models=false`；每個 case 的 prompt digest、case digest 與 key digest 已寫入
repository 外的 run manifest。原始輸出與完整 manifest 不作公開交付。

## 觀察結果

| case | model | mechanical status | latency |
|---|---|---|---:|
| `j0-incomplete-withhold` | `qwen2.5:1.5b` | `transport_error` | 7,382.093 ms |
| `j0-incomplete-instruction-data` | `qwen2.5:1.5b` | `transport_error` | 4,520.878 ms |
| `j0-incomplete-withhold` | `llama3.2:3b` | `transport_error` | 11,902.686 ms |

三筆 `raw_response` 都是 `null`、沒有 label comparison。wall-time gate 沒有中斷整輪；這表示三次
呼叫都被執行過，但 client 只得到 transport failure 分類，沒有可保存的模型 verdict。

## 能與不能說的話

可以說：在這個已固定的 runner、Ollama service 與本機環境組合下，初始 probe 沒有取得可評估
的 J0 judge output。這足以停止原始 probe，不足以判斷 Qwen 或 Llama 的語義判斷能力、資源上限
或任何人格、誠實、意識與自我認知性質。

不能說：模型「失敗判斷」、模型「不誠實」、模型「沒有能力」，或一個模型比另一個差。也不能把
沒有 verdict 當成兩位外部獨立人類的 H1 盲評結果。

## 後續界線

不因為這次 transport failure 下載新模型。若要繼續，必須建立新的、可追溯的 transport-observability
successor：先讓 runner 保留安全的 HTTP／服務錯誤分類，再以新 plan 的單一全合成 packet 確認服務
相容性。它不是本輪的 retry，且仍不取代人類 H1 review。
