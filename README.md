# Accountable Dialogue／有帳對話

> A public accountability and evidence layer for consequential AI dialogue.

Accountable Dialogue does not try to make an AI *look* like it has an inner life.
It asks a narrower and more testable question: when a consequential claim,
commitment, decision, correction, or system change is made, can another person
later determine what changed, why, on whose authority, with what evidence, and
what remains unproven?

目前這是一個**文件先行的公開基線**，尚未宣稱具備可部署的 runtime、訓練系統或資料集。

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
- [公開邊界](PUBLIC_BOUNDARY.md)：什麼可以進公開倉庫，什麼必須留在受限環境。
- [研究邊界：可問責的認識論行為](docs/research/behavioral-honesty-research-boundary.md)：若要研究「誠實相關行為」，什麼才是可測的問題。
- [任務板](task.md)：目前已接受的工作與尚待擁有者決定的事項。

## 最小模型

每筆紀錄先區分它是 `Observation`、`Claim`、`Proposal`、`Commitment`、
`Decision`、`Evidence`、`Artifact`、`Verification` 或 `Event`；再分別描述它的
治理、工程、驗證與生命週期狀態。

這避免兩種常見誤導：把好想法說成已實作，或把通過測試說成已證明其效果。

## 公開承諾

1. 不以漂亮敘事代替可檢查的改動。
2. 不把對話中的提案悄悄升格成永久規則。
3. 不以可追溯性為名收集或公開不必要的私人資料。
4. 不以「模型很誠實」或「模型有內在」作為未經驗證的產品宣稱。

## 目前狀態

- Repository state: `foundational / documentation-first`
- Runtime implementation: `not_implemented`
- Dataset or training program: `not_implemented`
- License: 尚未選定；在擁有者明確選擇前，不應假設可重用條款。

> 不替系統宣稱靈魂；只要求它對影響負責。
