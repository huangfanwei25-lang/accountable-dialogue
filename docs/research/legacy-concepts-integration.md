# 舊概念整合邊界

> 文件類型：設計 lineage／非遷移聲明<br>
> 治理狀態：`under_review`<br>
> 工程狀態：`not_implemented`<br>
> 驗證狀態：`not_applicable`

本文件記錄一次受限的只讀考察：舊 ToneSoul 專案可作為思考燃料，但不是可直接搬入
Accountable Dialogue 的公開來源。沒有舊 Git history、程式、私人記憶、日誌、prompt、
模型參數或自動化機制被複製到本倉庫。

## 可重寫的設計教訓

| 舊概念的教訓 | 在本倉庫的公開重寫 | 不可推得的結論 |
|---|---|---|
| 張力可揭露衝突、證據不足或立場摩擦 | 未來可作有方法、範圍與限制的 `runtime_observation` evidence | 張力值是誠實度、情緒或靈魂分數 |
| 承諾遭挑戰後應保留原因與退出歷史 | `Commitment` 是 subject；`withdrawn`／`superseded` 是後來事件 | 自動偵測到的矛盾已構成真實修正 |
| provenance 或 hash chain 能暴露部分完整性問題 | 後續私有持久化若被授權，可另附 Artifact／evidence 指標 | hash、簽章或 trace 證明真值、人身或權限 |
| 記憶升格應有證據與審查門檻 | 權限、證據、實作與驗證需分開記錄 | 規則或 Council 同意可以取代人類治理定案 |
| 記憶主權與同意是邊界 | 只保留公開最小摘要；不把原始對話當預設材料 | 去識別化一次就永遠沒有再識別風險 |
| 少數意見與失敗應保留 | `challenges`、`limits`、撤回與 successor 可留在可檢查歷史 | 多數一致或敘事連貫等於正確 |

## 已使用與尚未使用

本次只把上述教訓轉成：

- `change-case-v0` 中 subject／event 的分離；
- 一個合成的 Commitment withdrawal 案例；
- [可問責的代理連續性 Proposal](accountable-agent-continuity-v0.md) 的觀察向量與反例；
- 公開資料最小化與 human authority boundary。

目前**沒有**引入 runtime、記憶庫、向量檢索、張力公式、人格參數、評分權重、簽章服務、
LLM 編排、模型訓練、資料集或自動規則更新。

## 後續門檻

若未來需要任何持久化或執行元件，必須先指出它解決的具體、未被現有 Schema／文件解決
的問題，再定義資料所有權、公開／私有限制、失敗模式、刪除程序、效能成本與測試。舊庫
中存在某種機制，不能單獨構成新庫的實作理由。
