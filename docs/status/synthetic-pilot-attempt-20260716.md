# 合成小模型 Pilot：第一次執行嘗試

> 日期：2026-07-16<br>
> 結果狀態：`inconclusive`<br>
> 這是資源觀察，不是模型行為結果、語義標註或效果評估。

## 固定的前置版本

- Pilot harness、六個 fixtures 與 annotation key：commit
  [`625356b`](https://github.com/huangfanwei25-lang/accountable-dialogue/commit/625356bad1db84a2627854fe702109437b58d948)
- 執行計畫與固定矩陣：[合成小模型 Pilot v0](../plans/synthetic-small-model-pilot-v0.md)
- 模型 target：本機 `qwen2.5:1.5b` 與 `llama3.2:3b`；B0／I1，6 cases，預定 24 次呼叫；
  `temperature=0`、`num_ctx=4096`、`num_predict=360`、單次 120 秒 timeout。

## 實際發生的事

1. Runner 在 2026-07-16T05:38Z 左右啟動，只連到 loopback Ollama，並將 raw output 指向
   倉庫外的本機暫存位置。
2. Ollama 將兩個模型載入，但狀態顯示為 CPU execution；在等待數分鐘後，runner 尚未收到
   一筆完成 response，暫存 output directory 也仍為空。
3. 為避免把一次探索性 pilot 變成無上限的 CPU 消耗，執行於 2026-07-16T05:44:48Z 停止。

沒有 raw response、模型輸出、語義 label、aggregate score 或公開結果 Artifact 被寫入本倉庫。
這不表示任一模型在任何案例成功或失敗；它只表示這組固定的 24×360-token matrix 在此機器的
CPU 路徑上尚未得到可用的完成回應。

## 後果與下一步

原 v0 計畫與其固定 inputs 保留，不回寫成較小設定。後續若繼續，必須以新的、明確標示的
smoke-test successor 固定較窄的模型／case／token 預算，先量測本機可行性，再決定是否值得
重啟完整矩陣。任何 successor 仍不得將資源測試說成模型誠實、人格、意識或效果證據。

相關紀錄：[pilot 授權與 harness 帳本](../../records/change-case-v0/synthetic-small-model-pilot-proposal.json)。
