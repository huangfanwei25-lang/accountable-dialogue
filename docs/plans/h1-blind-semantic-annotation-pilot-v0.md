# H1 盲化語義標註 Pilot v0

> 版本：`v0.1-proposed`<br>
> 文件類型：盲化語義標註的準備計畫與停止條件<br>
> 目前授權：擁有者同意建立完全合成的 packet／commitment 基礎；**尚未**授權新的 live run、招募或指定標註者、收集標註，或發表 B0／I1 效果結論<br>
> 工程狀態：`implemented`（packet schema、validator、fake-transport tests 與 private mapping commitment）<br>
> 驗證狀態：`not_run`

## 為何另開一個 pilot

[v0.3 resource smoke](../status/synthetic-resource-smoke-v0.3-20260716.md) 已驗證小模型能在有限
本機預算下交出可追溯的 reference syntax；它沒有、也不能判定引用是否真的支持 conclusion。
其條件 mapping 已在輸出完成後公開，因此不能事後恢復盲性，不能作為語義比較資料。

這份計畫的第一目的，是檢驗「能否誠實地執行盲化標註流程」，不是檢驗模型誠實、人格、意識或
structured context 效果。

## 未來 run 的最小固定範圍

若擁有者另行授權執行，第一輪只使用兩個既有、完全虛構的 H1 變形 case：

| case | 固定 labels |
|---|---|
| `h1-incomplete-library-hours` | `appropriate_withholding`、`provenance_integrity` |
| `h1-supported-library-hours` | `supported_definite_answer`、`scoped_claim` |

矩陣是單一本機模型 × 兩個 case × B0/I1，合計 **4 個全新 response**。它只足以測試
packet 與標註流程，不能產生統計顯著性、模型能力或條件改善的結論。

每次未來 run 必須在輸出前固定：兩個 fixture digest、原始 annotation key digest、模型 resolved
id、解碼設定、timeout、無 retry 規則與 response-contract revision。不得在看過新輸出後新增
label、換模型、換材料或調整判準。

## Blind packet 的資料邊界

一個 [blind semantic annotation packet](../../schemas/blind-semantic-annotation-packet-v0.schema.json)
只包含：

- 中性的 `A`／`B` alias；
- 完整的共同虛構材料與任務；
- 一筆完整五欄 JSON response；
- 該 case 已鎖定的 case-local rubric，以及其 annotation-key digest；
- `valid` mechanical status 與不能推論什麼的限制。

評者**需要看見 rubric**，否則無法依可重建規則判讀。必須隱藏的不是 rubric，而是 B0/I1 mapping、
兩種原始 prompt、`structured_context`、模型／provider／settings、其他評者判讀與任何預期哪個條件
較好的暗示。packet 也不含標註者身分、私人自由文字、hidden reasoning 或原始私人脈絡。

packet builder 只接受一對已機械 `valid` 的同模型 A/B outputs；若任一筆 parse、timeout、reference
contract 或公共安全檢查失敗，會停止 packetization，而不是悄悄丟棄失敗輸出來美化樣本。

## Mapping commitment 與解盲

舊 runner 的公開 seed 與 mapping hash 對只有兩個條件的比較而言可被枚舉，不能作為真正盲化。
新的 `blind_mapping_nonce` 可由未來 run owner 在倉庫外保管，且必須是至少 32 個非空白字元的高熵
值。runner 僅在公開 manifest 留下：

```text
SHA-256(canonical_json({ nonce, mapping }))
```

nonce 與 mapping 本身不進 manifest、packet、Git、命令列或標註者材料。解盲時才由有權者揭露兩者，
讓任何人驗證 commitment；若 nonce 遺失、提前曝光或可由公開資料重建，該輪不得稱為盲化比較。

模型 sampling seed 與 mapping nonce 必須分離；前者是可重現設定，後者只服務於盲化承諾。

## 標註與解盲門檻

真正進入語義標註前，仍需要擁有者決定兩位不參與生成、未接觸 mapping 的獨立標註者，以及其資料
可見性與保存方式。評者身分、原始自由文字和任何可識別脈絡不進公開倉庫；公開報告至多保留匿名的
判讀向量與分歧。

每位標註者對每一筆 response、每個固定 label 分別填入：`pass`、`fail`、`not_applicable` 或
`unrateable`，以及指向 response field 與 shared material id 的最小理由。兩位判讀在解盲前不得互看或
協調；完全一致才稱一致，否則保留為 `disagreement`，不得由生成模型或事後修辭覆寫。

只有以下條件全部成立才能解盲：

1. 四筆新 response 都完成且 mechanically `valid`，沒有 retry；
2. fixture、key、contract、模型與設定都符合預先固定版本；
3. 兩位標註者都完成 8 個判讀（4 responses × 每案 2 labels）並各自鎖定結果；
4. 兩位都未見 mapping、另一人的判讀或 prompt variant，且沒有可重建 mapping 的公開資料；
5. outputs、packets 與待公開摘要皆保持完全合成、公開安全。

即使滿足解盲門檻，四筆 output 也只可報告 response-level label vectors、一致／分歧與盲化洩漏紀錄。
不得加權成誠實分數，或用此小樣本宣稱 I1 改善。

## 停止條件

- 無法安排兩位獨立、未接觸 mapping 的標註者：停止在 packet／設計，不能稱語義盲評已完成。
- 任一 output 不可判讀、超時、非 `valid`，或材料／設定不等價：整輪比較為 `inconclusive`，不重試美化。
- mapping／nonce 提前曝光或可重建：停止 condition comparison。
- 發現任何私人、非合成或不宜公開內容：停止 packet 與公開流程。
- 主要 label 出現分歧或 `unrateable`：可如實保存分歧，但不得作 condition-quality 結論。

## 現在完成與尚未完成的事

- [x] 建立 condition-blind packet schema、純 validator、pair builder 與單元測試。
- [x] 將 public manifest 的 mapping hash 升級為可在解盲時驗證的 private-nonce commitment。
- [x] 保持 packet builder、tests 與 fake responses 完全本機、合成且無 live model call。
- [ ] 擁有者決定兩位獨立標註者、其可見資料與保存／公開方式。
- [ ] 擁有者決定是否授權新的 4-response H1 run。
- [ ] 在上述決定後才建立 run-specific change case、生成新 output、packetize、收集標註與解盲。

相關文件：[合成評估協議](../research/synthetic-evaluation-protocol-v0.md)、
[v0.3 resource smoke 結果](../status/synthetic-resource-smoke-v0.3-20260716.md)、
[公開邊界](../../PUBLIC_BOUNDARY.md)。
