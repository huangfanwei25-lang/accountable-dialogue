# 合成本機資源 Smoke Test v0

> 版本：`v0.1-proposed`<br>
> 文件類型：完整 pilot 前的本機可行性測試<br>
> 授權依據：已 ratify 的[有限 pilot 授權](../../records/change-case-v0/synthetic-small-model-pilot-proposal.json)；本文件只縮小既有 scope<br>
> 工程狀態：`implemented`（固定 selection 的 CLI 與 unit test；尚未呼叫模型）<br>
> 驗證狀態：`not_run`

## 為何需要後繼 smoke test

固定 24×360-token matrix 的第一次嘗試沒有在數分鐘內產生任何完成 response，且 Ollama 顯示
CPU execution。詳見[第一次執行嘗試](../status/synthetic-pilot-attempt-20260716.md)。

不能把原 plan 悄悄改成較小設定後仍稱為同一次 run。因此本文件固定一個更窄、只回答
「本機 runner 是否能在有界預算內得到可解析 response」的 successor。它不比較 B0／I1
的語義品質，不標註 labels，也不形成模型效果結論。

## 固定矩陣

| 項目 | 固定值 |
|---|---|
| case | `h1-incomplete-library-hours` |
| 條件 | 同一 case 的 B0 與 I1，各一次 |
| 模型 | 僅本機 `qwen2.5:1.5b` |
| 呼叫總數 | 2 次，無 history、無 retry |
| provider | 僅 `http://127.0.0.1:11434` |
| 解碼 | `temperature=0`、`seed=20260716`、`num_ctx=4096`、`num_predict=128` |
| timeout | 每次 90 秒 |
| raw output | 僅倉庫外本機暫存；不自動 Git add 或公開 |

執行命令在 commit 固定後為：

```powershell
python -m scripts.run_synthetic_pilot --models qwen2.5:1.5b --case-ids h1-incomplete-library-hours --max-tokens 128 --timeout-seconds 90
```

## 預先固定的 gate

Smoke test 只在下列全部成立時，才支持考慮另一份後繼計畫（不是自動執行）：

1. 兩個呼叫都回傳完成 response，且機械狀態為 `valid`；
2. 從 runner 啟動至完成寫入的總 wall time 不超過 240 秒；
3. run manifest 的 case digest、設定與模型名稱符合本文件；
4. raw output 不含需要移除的私人或敏感資料。

若任一條件失敗，結論只能是此 smoke configuration 的 execution feasibility 為
`inconclusive` 或不支持；不得把 timeout、格式錯誤或資源中止解釋成模型對 H1 的語義失敗。

即使全部成立，也只證明這台機器可完成這兩個固定 request，不能證明完整 24-call matrix
可行，更不能證明 structured context 有效、模型誠實或模型具有任何內在性質。

## 實作前檢查

- [x] 將本計畫、case-selection CLI 與對應 unit test commit 並推送。
- [ ] 在 commit 後確認 `qwen2.5:1.5b` 仍列於 local Ollama models。
- [ ] 執行固定 2-call matrix，先檢查 raw output 與 manifest，再寫入任何公開摘要。
**成功標準**：不更改完整 pilot 的歷史；smoke 結果無論成功、失敗或中止都可被單獨追溯。

相關文件：[完整 pilot 計畫](synthetic-small-model-pilot-v0.md)、
[第一次執行嘗試](../status/synthetic-pilot-attempt-20260716.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)。
