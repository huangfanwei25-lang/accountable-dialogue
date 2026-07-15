# 公開面遷移清單 v0

> 文件類型：`Proposal`<br>
> 治理狀態：`under_review`<br>
> 工程狀態：`not_implemented`<br>
> 驗證狀態：`partially_verified`（已完成來源分類，尚未實作候選切片）<br>
> 生命週期：`active`

## 目的

這不是「把舊倉庫搬過來」的清單。它規定新倉庫只帶走可重新檢查的概念骨架，並以新名稱、新邊界、新測試重新建立 Artifact。舊資料、舊歷史與舊自動化不能因為曾經公開就自動取得遷移資格。

## 分類結果

### 已可公開的基線

| Artifact | 決定 | 理由 |
|---|---|---|
| `LICENSE` | 保留 | 擁有者已在新倉庫選擇 Apache-2.0。 |
| README、公開邊界、哲學／工程契約、研究邊界 | 新寫並保留 | 它們描述新倉庫的範圍，不依賴舊 runtime 或舊歷史。 |
| 可觀測性與證據邊界 | 新寫並保留 | 保留「trace 不等於隱藏推理」與「權限不等於證據」的概念，不帶入舊系統術語。 |

### 可以重寫，但現在不直接實作

| 候選 | 新形式 | 為何不直接複製 |
|---|---|---|
| 事件／決策紀錄 | `change-record-v0` 的新 schema、合成範例與 validator | 舊格式混入舊路徑、歷史主張、來源與語義；有事件存在不等於內容為真。 |
| 證據階梯 | 本倉庫的證據種類與驗證範圍 | 舊編號、測試數字與 runtime 主張不能移植成新事實。 |
| 主張權限矩陣 | 小型 claim-record 範例 | 巨大靜態矩陣會把舊政策偽裝成新倉庫的規則。 |
| 異議與撤回 | decision-record 的可選欄位與 supersession 連結 | 先驗證最小資料模型，再決定是否需要審議或持久化服務。 |
| 原則的可挑戰性 | support／falsifier／non-falsifier／response 模板 | 不帶入舊本體論或以哲學取代可觀察證據。 |

### 絕不遷移到此公開面

- 原始對話、私人／共同觀察事件、記憶、session journal、向量庫與可重識別脈絡；
- 歷史 trace dataset、事件帳本、編年史與自動生成狀態檔；
- 舊 runtime、LLM 編排、人格／自我模型、記憶淬鍊或自動規則更新程式；
- 深度攻擊 payload、真實防禦閾值、部署憑證與私有 prompt；
- 以靈魂、自我、意識或已學會誠實為核心的舊命名與能力敘述；
- 文字編碼已損壞、來源不明或無法重現的舊文件。

## 第一個候選能力：`change-record-v0`

這是候選，不是已接受的 roadmap。它的目的只是驗證哲學契約是否能落在一筆小型、無私人內容的資料上。

最小公開欄位應包含：

```text
id
record_type
created_at
public_summary
authority { status, role, reference? }
artifacts[]
evidence[]
governance_status
engineering_status
verification_status
lifecycle_status
supersedes?
visibility
```

初版不得要求或預設接受：原始對話、隱藏推理、email、token、自由輸入的私人脈絡、未去識別化 actor 身分，或「模型真實意圖」欄位。

若擁有者 ratify 此候選，實作順序應為：

1. 新寫 JSON Schema，不複製舊 schema；
2. 新寫兩筆合成範例：一筆 Proposal、一筆 Withdrawal／Supersession；
3. 新寫標準函式庫 validator 與測試；
4. 測試缺欄位、非法狀態、private-looking payload 與不合法 supersession；
5. 僅在通過後才討論 CLI、儲存、資料集或 runtime 整合。

## 尚待擁有者定案

1. 是否 ratify 現有的哲學／工程契約與可觀測性詞彙？
2. `change-record-v0` 是否值得成為第一個程式切片？
3. 若未來有資料，哪些欄位可以公開、哪些只能受限存取、哪些不應收集？
4. 是否需要獨立的私有研究面；若需要，公開倉庫只保留協議與去識別化評估方式。

## 現在的結論

目前不需要再上傳舊程式碼或資料。下一個有價值的公開變更，應是小而可測的 `change-record-v0`，而不是另一個龐大的 AI 系統。
