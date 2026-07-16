# Accountable Dialogue／有帳對話

> A public accountability and evidence layer for consequential AI dialogue.

Accountable Dialogue does not try to make an AI *look* like it has an inner life.
It asks a narrower and more testable question: when a consequential claim,
commitment, decision, correction, or system change is made, can another person
later determine what changed, why, on whose authority, with what evidence, and
what remains unproven?

目前這是一個**文件先行、帶有最小本機 prototype 的公開基線**。它尚未宣稱具備可部署的
runtime、訓練系統、資料集、身份服務或持久化帳本。

## 它是什麼

- 讓重要改動留下理由、Artifact、證據、權限、後果與驗證範圍；
- 讓提案、定案、實作與驗證不再被同一個「完成」混在一起；
- 讓撤回與修正可追溯，同時保護不應公開的私人脈絡；
- 為未來可檢驗的 AI 協作治理與研究建立共同語言。

## 它不是什麼

- 不是關於意識、靈魂或主觀自我的宣稱；
- 不是對隱藏推理的存取或公開機制；
- 不是一個全域「誠實分數」，也不是已證明能從語料教會模型誠實的訓練器；
- 不是保存一切對話、記憶或私人資料的理由。

## 起始文件

- [哲學／工程契約](docs/philosophy/engineering-contract.md)：重要改動、權限、撤回、風險與完成聲稱的共同規則。
- [可觀測性與證據邊界](docs/contracts/observability-and-evidence-boundary.md)：哪些東西可被檢查，哪些仍必須誠實稱為不透明。
- [公開邊界](PUBLIC_BOUNDARY.md)：什麼可以進公開倉庫，什麼必須留在受限環境。
- [研究邊界：可問責的認識論行為](docs/research/behavioral-honesty-research-boundary.md)：若要研究「誠實相關行為」，什麼才是可測的問題。
- [可問責的代理連續性 v0](docs/research/accountable-agent-continuity-v0.md)：將誠實、記憶、人格與治理拆成可反駁的研究問題，而非一個靈魂或誠實分數。
- [合成評估協議 v0](docs/research/synthetic-evaluation-protocol-v0.md)：在不收集私人對話、不訓練模型的前提下，定義未來如何測試候選行為；仍待審查。
- [合成評估案件候選格式 v0](docs/design/synthetic-evaluation-case-v0.md)：先把虛構案例、labels 與 run 結果分開；它不是 Schema、資料集或 evaluator。
- [合成小模型 Pilot v0](docs/plans/synthetic-small-model-pilot-v0.md)：獲授權的 6-case、兩條件、兩個本機小模型探索；結果尚未產生。
- [舊概念整合邊界](docs/research/legacy-concepts-integration.md)：只重寫可公開的設計教訓，不搬入舊記憶、日誌或 runtime。
- [公開面遷移清單](docs/plans/public-surface-intake-v0.md)：哪些舊素材只取其概念、哪些必須重寫、哪些絕不搬入。
- [變更案件模型 v0](docs/design/change-case-v0.md)：第一個公開原型如何區分事項、依據、事件與唯讀投影。
- [公開變更案件紀錄](records/change-case-v0/change-case-v0-prototype.json)：這個原型自身的 Artifact、證據、權限宣告與限制。
- [任務板](task.md)：目前已接受的工作與尚待擁有者決定的事項。

## 最小模型

先區分四個不能混在一起的問題：

- **事項（subject）**是什麼：例如 `Observation`、`Claim`、`Proposal` 或 `Commitment`；
- **依據（artifact / evidence）**可核對什麼；
- **事件（event）**這次發生什麼：例如送審、定案、驗證、撤回或替換；
- **投影（projection）**目前的事件歷史能支持什麼描述。

例如，`Proposal` 是被處理的事項；它被另一個版本取代，是後來發生的
`superseded` 事件。定案權描述的是某個治理事件由誰依何種範圍作出，不能被寫成
另一個模糊的狀態欄位。治理與終止生命週期不以最後一筆靜默覆寫；可重複的實作與
驗證事件則保留全歷史，投影只顯示 canonical sequence 中最新的報告及其來源 event id。

這避免三種常見誤導：把好想法說成已實作、把通過測試說成已證明效果，或把
有權者的決定誤寫成效果證據。

## 公開承諾

1. 不以漂亮敘事代替可檢查的改動。
2. 不把對話中的提案悄悄升格成永久規則。
3. 不以可追溯性為名收集或公開不必要的私人資料。
4. 不以「模型很誠實」或「模型有內在」作為未經驗證的產品宣稱。

## 目前狀態

- Repository state: `foundational / small validated prototype`
- Change-case prototype: local Schema、validator 與唯讀 projection；三個合成案例與一筆可檢查的 repository record
- Deployable runtime, storage, or identity service: `not_implemented`
- Dataset or training program: `not_implemented`
- License: [Apache-2.0](LICENSE)，由公開倉庫初始化時的擁有者選擇。

> 不替系統宣稱靈魂；只要求它對影響負責。
