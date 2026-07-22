# 跨模型可問責連續性 Profile v0

> 版本：`v0.1-proposed`<br>
> 文件類型：公開整合契約／投影 Profile<br>
> 治理狀態：`under_review`<br>
> 工程狀態：`documented_not_integrated`<br>
> 本 Profile 唯一跨倉庫公共交換協議：`accountable-dialogue/change-case-v0`

相關文件：[公開邊界](../../PUBLIC_BOUNDARY.md)、[哲學／工程契約](../philosophy/engineering-contract.md)、[Change Case v0](../design/change-case-v0.md)、[JSON Schema](../../schemas/change-case-v0.schema.json)。

## 目的

這份 Profile 定義模型、工具或 runtime 更換時，哪些**公開且可核對的語義**可以延續。
它讓接手者知道目前有哪些承諾、張力與限制，卻不把外部紀錄說成模型權重中的記憶、
主觀經驗、持續 identity 或可讀取的內在思維。

它不是新的資料模型。本 Profile 的跨倉庫公開交換只使用既有、帶版本的 JSON contract：
`accountable-dialogue/change-case-v0`。本文件列出的是如何安全使用該協議的 Profile，
不新增第二套 continuity schema、狀態軸或可寫入的「人格」欄位。

## 三層所有權

| 層級 | 擁有什麼 | 不擁有什麼 |
|---|---|---|
| **Accountable Dialogue** | 公開、通用的 ChangeCase 協議、驗證器、測試，以及由事件歷史導出的 public-safe projection | 私人記憶內容、ToneSoul runtime、模型身份或治理定案權 |
| **Private Memory** | 由擁有者選擇、授權、可撤回的私人連續性；其存取與保留受自身政策管理 | 不因與本協議相容就取得公開權限，也不自動成為 Accountable Dialogue 的輸入 |
| **ToneSoul** | runtime／consumer、領域語彙、互動流程，以及把已授權事件映射為 ChangeCase 的 adapter | 不重新定義通用公開協議，也不藉 adapter 越過私人資料或治理邊界 |

倉庫之間預設**沒有自動同步**。Accountable Dialogue 不拉取、不掃描也不要求 Private
Memory；ToneSoul 不得把可讀取誤認為可公開。任何私人資料匯入或公開投影都需要另一次
明確授權與最小化審查，不能由檔案存在、模型稱讚或先前對話推定。

## 初期整合介面

初期只交換通過公開邊界檢查的 `accountable-dialogue/change-case-v0` JSON 檔案：

1. producer 明確寫入 `format` 版本並依固定版本的
   [`schemas/change-case-v0.schema.json`](../../schemas/change-case-v0.schema.json) 驗證；
2. 人類或其明確授權者先確認投影符合 [`PUBLIC_BOUNDARY.md`](../../PUBLIC_BOUNDARY.md)；
3. consumer 驗證版本與語義規則，把內容當成可核對紀錄，而非真理、權限或身份證明；
4. 不相容版本快速失敗，不以猜測欄位、靜默降級或最後寫入勝出來修補。

初期不建立直接 Python package dependency。Accountable Dialogue 與 ToneSoul 可以有不同的
Python 版本、發布節奏與依賴邊界；用版本化 JSON contract 讓 producer 與 consumer 各自在
自己的環境驗證，比跨倉庫直接 import 更容易測試與撤回。這項選擇不代表永遠禁止 SDK，
只表示 SDK 必須在相容性與版本政策有獨立證據後另案審查。

交換面不得包含原始私人對話、私人記憶本文、憑證、本機絕對路徑、向量資料、
chain-of-thought、被稱為「內部思維」的內容，或用來繞過安全邊界的私有參數。

## 可公開的 deliberative stance

`deliberative stance` 是事件歷史支持的**唯讀審議立場投影**，不是 personality、identity、
靈魂分數或新的可寫狀態。公開投影只應保留完成問責所需的最小內容：

- **承諾**：目前仍有效、且已有公開事件依據的 Commitment；
- **未解張力**：互不相容但尚未被治理決定消除的要求；
- **不確定性**：證據不足、資料缺口或驗證範圍；
- **風險**：會影響可逆性、安全、隱私、成本或責任的已辨識條件；
- **禁止推論**：現有資料不能支持的結論；
- **改變條件**：哪些新證據、事件或授權會使目前投影需要修訂。

以上名稱是公開審查維度，不是 `change-case-v0` 的新欄位。它們只能由既有的 subject、
artifact、evidence、event 與 projection 關係表達，並保留來源 event id；不得另建一份會與
事件歷史分岔的「內在狀態」。

模型可以提出 stance 摘要與反例，但不能把摘要自行升格為治理決定。不同模型讀到相同
JSON 仍可能產生不同詮釋；本 Profile 要求的是可回查來源與顯示分歧，不宣稱生成結果一致。

## Resource observation 邊界

資源觀測只有兩種公開狀態：

- `reported`：工具或 provider 在可引用的介面中明確回報一項度量；
- `not_reported`：沒有可引用的回報，或回報不包含正在詢問的度量。

`reported` 紀錄至少要保留來源、觀測時間、原始 metric 名稱、值、單位與適用範圍。只有來源
明確回報時才能記錄 limit、used 或 remaining；不得用對話長度、感覺、累計使用量或其他替代
訊號推測 token budget。來源沒有總量時，remaining 就是 `not_reported`，不是零，也不是無限。

資源觀測描述的是一次工具／執行環境事件。它不證明模型能感受疲勞、知道自己的完整運算
狀態、擁有持續 identity，或能在「最後一點算力」自動切換治理權限。

## 接手與失敗規則

新模型接手時應先核對協議版本、Artifact、事件順序、授權範圍、禁止推論與未解張力；找不到
資料時應留下缺口。它不得：

- 以自己的合理推測補成舊模型的記憶；
- 把 public-safe projection 反推為私人原文或 chain-of-thought；
- 把跨模型相似回答宣稱為同一個主觀自我；
- 因 producer 能讀取另一個倉庫，就執行自動同步或私人資料匯入；
- 因資源狀態是 `not_reported`，就假造 remaining token budget。

## v0 驗收範圍

這份切片完成時只能宣稱：三層責任、公開 stance、資源觀測與跨模型入口已有文件與靜態測試。
它不能宣稱 Private Memory 已接線、ToneSoul 已整合、模型間語義必然一致、身份得以延續，或
任何模型因此變得更誠實。這些都需要各自的 Artifact、授權、整合測試與驗證紀錄。
