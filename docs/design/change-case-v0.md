# 變更案件模型 v0

> 版本：`v0.1-proposed`<br>
> 文件類型：第一個公開程式切片的設計<br>
> 授權範圍：擁有者已允許製作有界 prototype；整體契約仍為 `under_review`<br>
> 工程狀態：`implemented`（本機 Schema、validator 與唯讀 projection）<br>
> 驗證狀態：`verified_within_scope`（兩個合成案例與拒絕規則）

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

治理定案也是 Event。它有 `decision.outcome`、`decision.made_by` 與
`decision.authority_basis`：

- `made_by` 是實際承擔決定的人；
- `authority_basis` 是其權限的類型、範圍與必要時的委派參照；
- 不存在 `authority.status`；權限不是又一個模糊的完成狀態。

v0 只允許 human owner 或 explicit delegate 作出 `ratified`／`rejected` 的治理決定。
代理可提出、記錄、驗證或附上證據，但不能藉由格式自行定案。

### 4. Projection：唯讀的目前描述

Schema 的輸入不含 `governance_status`、`engineering_status`、`verification_status`、
`lifecycle_status` 或可原地覆寫的 `supersedes`。應由事件排序後推導：

| 投影 | 起始／缺口 | 來源 |
|---|---|---|
| governance | `no_governance_record` | review 與最後一筆治理決定事件 |
| lifecycle | `no_terminal_event` | withdrawn、superseded、archived 等事件 |
| implementation | `no_implementation_report` | implementation_reported 事件 |
| verification | `no_verification_record` | verification_recorded 事件 |

這些是介面可顯示的讀取結果，不是可單獨寫入的真相。日後若快取，必須能由案件重新
計算；帳本的缺口不可以偽裝成系統對現實的否定斷言。

## v0 的非目標

- 不做資料庫、網路 API、登入、委派服務或存取控制；
- 不保存原始對話、hidden reasoning、prompt、token、email 或本機絕對路徑；
- 不證明自由文字完全沒有個資；只拒絕已知敏感欄位與部分明顯格式；
- 不把有權者的定案當成實作、品質或效果的證據；
- 不宣稱這個外骨骼能讓模型擁有內在誠實。

## 驗收方式

公開 prototype 包含 JSON Schema、兩個合成案例、純標準函式庫 validator 與測試。
目前測試接受 Proposal／治理定案與 Verification／Supersession，並拒絕：

1. 在 subject 上直接寫 lifecycle 或 governance status；
2. `authority.status` 或 agent 自行作出的治理定案；
3. 不存在的參照、self-supersession 或沒有 successor 的替換事件；
4. raw dialogue、hidden reasoning、prompt、token、email 或絕對本機路徑。

相關文件：[哲學／工程契約](../philosophy/engineering-contract.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)、[公開面遷移清單](../plans/public-surface-intake-v0.md)。
