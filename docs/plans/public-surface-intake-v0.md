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
| 變更案件 | `change-case-v0` 的新 schema、合成範例與 validator | 一個案件分開保存事項、依據與事件；舊格式把它們混成單筆 record。 |
| 證據階梯 | 本倉庫的證據種類與驗證範圍 | 舊編號、測試數字與 runtime 主張不能移植成新事實。 |
| 主張權限矩陣 | 小型 claim-record 範例 | 巨大靜態矩陣會把舊政策偽裝成新倉庫的規則。 |
| 異議與撤回 | 具明確 subject 參照的事件與 successor 連結 | 先驗證最小資料模型，再決定是否需要審議或持久化服務。 |
| 原則的可挑戰性 | support／falsifier／non-falsifier／response 模板 | 不帶入舊本體論或以哲學取代可觀察證據。 |

### 絕不遷移到此公開面

- 原始對話、私人／共同觀察事件、記憶、session journal、向量庫與可重識別脈絡；
- 歷史 trace dataset、事件帳本、編年史與自動生成狀態檔；
- 舊 runtime、LLM 編排、人格／自我模型、記憶淬鍊或自動規則更新程式；
- 深度攻擊 payload、真實防禦閾值、部署憑證與私有 prompt；
- 以靈魂、自我、意識或已學會誠實為核心的舊命名與能力敘述；
- 文字編碼已損壞、來源不明或無法重現的舊文件。

## 第一個選定 prototype：`change-case-v0`

擁有者已允許這個有界 prototype，但資料模型與整體哲學契約仍可受審查。
這個名稱刻意不用「萬用 record」：它是一個小型、有界的變更案件。它的目的只是驗證
哲學契約是否能落在無私人內容的資料上，不是建立全域記憶、資料庫或 runtime。

最小公開結構應分為：

```text
subjects[]  # Proposal、Claim 等「它是什麼」
artifacts[] # 可核對的版本或載體
evidence[]  # supports / challenges / limits 關係
events[]    # 這次發生什麼
projection  # 只能由上述紀錄衍生，不能作為真實來源
```

`Proposal` 是 subject 的 kind；`superseded` 是指向舊 subject 與 successor 的 event。
`authority.status`、`governance_status`、`lifecycle_status` 與可原地覆寫的
`supersedes` 都不進 v0 input。治理結果與權限依據屬於治理事件；介面上的狀態須由
事件歷史重算。

初版不得要求或預設接受：原始對話、隱藏推理、email、token、自由輸入的私人脈絡、
未去識別化 actor 身分，或「模型真實意圖」欄位。

若擁有者 ratify 此候選，實作順序應為：

1. 新寫 JSON Schema，不複製舊 schema；
2. 新寫兩筆合成範例：一筆 Proposal／治理定案、一筆 Verification／Supersession；
3. 新寫標準函式庫 validator 與唯讀 projection 測試；
4. 測試缺欄位、混淆層次的 status、private-looking payload 與不合法 supersession；
5. 僅在通過後才討論 CLI、儲存、資料集或 runtime 整合。

## 尚待擁有者定案

1. 是否 ratify 現有的哲學／工程契約與可觀測性詞彙？
2. `change-case-v0` 是否值得成為第一個程式切片？
3. 若未來有資料，哪些欄位可以公開、哪些只能受限存取、哪些不應收集？
4. 是否需要獨立的私有研究面；若需要，公開倉庫只保留協議與去識別化評估方式。

## 現在的結論

目前不需要再上傳舊程式碼或資料。下一個有價值的公開變更，應是小而可測的 `change-case-v0`，而不是另一個龐大的 AI 系統。
