# 變更案件模型 v0

> 版本：`v0.1-proposed`<br>
> 文件類型：第一個公開程式切片的設計<br>
> 授權範圍：擁有者已允許製作有界 prototype；整體契約仍為 `under_review`<br>
> 工程狀態：`implemented`（本機 Schema、validator 與唯讀 projection）<br>
> 驗證狀態：`verified_within_scope`（三個合成案例、repository record 與拒絕規則）

## 為何不叫作萬用 record

先前的 `change-record-v0` 工作名稱把「一筆資料」誤當成同一種東西，容易讓
`Proposal`、治理結果、`superseded`、證據與狀態欄位彼此覆寫。這個 prototype 改稱
`change-case-v0`：它是一個小型、可公開檢查的**變更案件**，不是全域記憶或資料庫。

它的問題是：對一個有影響的改動，哪些事項被處理、依據是什麼、這次發生什麼，以及
目前帳本能支持什麼描述？

```text
subjects ──────── Proposal / Claim / Commitment：它是什麼
   │
   ├── evidence ── supports / challenges / limits：憑什麼說
   ├── artifacts ─ 可定位的文件、程式或測試：可檢查什麼
   └── events ──── review / decision / verification / superseded：發生什麼
                         │
                         └── projection：唯讀地推導目前帳本說得出的狀態
```

## 四層資料

### 1. Subject：被處理的事項

`subject.kind` 只允許：`observation`、`claim`、`proposal`、`commitment`。

`Proposal` 留在這一層。它存在，不等於已送審、已定案、已實作或已驗證。

### 2. Artifact 與 Evidence：可核對的依據

Artifact 是可定位且帶版本或 digest 的文件、程式、Schema、測試或外部來源。Evidence
描述它如何 `supports`、`challenges` 或 `limits` 一個 subject。它們不是治理狀態，也不
因為有檔案就自動證明內容為真。

### 3. Event：這次發生什麼

初版事件包含：`subject_created`、`review_requested`、`governance_decided`、
`implementation_reported`、`verification_recorded`、`withdrawn`、`superseded` 與
`archived`。

`superseded` 事件必須同時指向 `previous_subject_id` 與 `successor_subject_id`。舊
subject 保留原文；新的 subject 才承載修正後的內容。

v0 不是讓 subject、治理或終止生命週期以「最後一筆覆寫前一筆」的容器。每個
subject 必須恰有一筆 `subject_created`，且任何後續事件都必須在它建立後才可引用它；
`review_requested` 必須先於唯一的 `governance_decided`；`withdrawn`、
`superseded` 與 `archived` 是互斥的終止事件。若真實情況需要重開、封存後再處置，
必須以未來明確的事件模型擴充，而非讓 v0 projection 無聲選取最後一筆。

實作與驗證是**可重複的報告事件**，不是終局狀態。`sequence` 是案件內的 canonical
ledger order，projection 依它顯示最新的 report outcome 與其 event id；`recorded_at`
不會取代這個順序，也不宣稱外部事件的精確發生時間。這個讀取結果不會刪除、合併或
把任何 report 誤稱為永久世界狀態；需要完整脈絡時，讀取所有 events。

治理定案也是 Event。它有 `decision.outcome`、`decision.made_by` 與
`decision.authority_basis`：

- `made_by` 是實際承擔決定的人；
- `authority_basis` 是其權限的類型、範圍與必要時的委派參照；
- 不存在 `authority.status`；權限不是又一個模糊的完成狀態。

v0 只允許 human owner 或 explicit delegate 作出 `ratified`／`rejected` 的治理決定。
代理可提出、記錄、驗證或附上證據，但不能藉由格式自行定案。

`authority_basis` 在 v0 是可供後續人工核對的**宣告**，不是身份驗證、簽章或委派服務。
validator 只限制其公開格式與角色組合；它不會也不能自行證明真實的人身、範圍或委派仍
然有效。

### 4. Projection：唯讀的目前描述

Schema 的輸入不含 `governance_status`、`engineering_status`、`verification_status`、
`lifecycle_status` 或可原地覆寫的 `supersedes`。應由事件排序後推導：

| 投影 | 起始／缺口 | 來源 |
|---|---|---|
| governance | `no_governance_record` | review 與唯一的治理決定事件 |
| lifecycle | `no_terminal_event` | withdrawn、superseded、archived 等事件 |
| implementation | `no_implementation_report` | canonical sequence 中最新的 `implementation_reported` 及其 event id |
| verification | `no_verification_record` | canonical sequence 中最新的 `verification_recorded` 及其 event id |

這些是介面可顯示的讀取結果，不是可單獨寫入的真相。日後若快取，必須能由案件重新
計算；帳本的缺口不可以偽裝成系統對現實的否定斷言。

## v0 的非目標

- 不做資料庫、網路 API、登入、委派服務或存取控制；
- 不把 `authority_basis` 的宣告誤稱為已驗證的身份或授權；
- 不保存原始對話、hidden reasoning、prompt、token、email 或本機絕對路徑；
- 不證明自由文字完全沒有個資；只拒絕已知敏感欄位與部分明顯格式；
- 不把有權者的定案當成實作、品質或效果的證據；
- 不宣稱這個外骨骼能讓模型擁有內在誠實。

## 驗收方式

公開 prototype 包含 JSON Schema、三個合成案例、純標準函式庫 validator 與測試。
目前測試接受 Proposal／治理定案與 Verification／Supersession，並拒絕：

1. 在 subject 上直接寫 lifecycle 或 governance status；
2. `authority.status` 或 agent 自行作出的治理定案；
3. 不存在的參照、self-supersession 或沒有 successor 的替換事件；
4. 缺少或重複建立事件、錯誤治理順序，以及會造成最後寫入覆蓋的終止事件；
5. raw dialogue、hidden reasoning、prompt、token、email、絕對本機路徑、路徑穿越或
   file URI。

## 對自己的紀錄

[`records/change-case-v0/change-case-v0-prototype.json`](../../records/change-case-v0/change-case-v0-prototype.json)
以同一個格式回溯記錄本 prototype 的 Artifact、證據、權限宣告與限制。它不是簽章、
身份服務或不可變帳本；`recorded_at` 是帳本事件被記錄的時間，未必等同外部工作最初
發生的時間。凡屬回溯記錄，摘要必須明示這一點，不能用精確 timestamp 假裝保有未曾
保存的即時歷史。

相關文件：[哲學／工程契約](../philosophy/engineering-contract.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)、[公開面遷移清單](../plans/public-surface-intake-v0.md)。
