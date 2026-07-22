# Accountable Dialogue：公開 AI 協作入口

本檔適用於所有在這個公開倉庫工作的 AI 與自動化工具。模型專用入口只能指向本檔，不能擴張權限或另立語義規則。

## 讀取順序

1. [README.md](README.md)：目的、現況與非宣稱。
2. [PUBLIC_BOUNDARY.md](PUBLIC_BOUNDARY.md)：公開資料的最高邊界。
3. [哲學／工程契約](docs/philosophy/engineering-contract.md)：提案、權限、事件與完成聲稱。
4. [跨模型可問責連續性 Profile v0](docs/contracts/cross-model-continuity-profile-v0.md)：跨模型接手與整合邊界。
5. [task.md](task.md)：只有已獲擁有者接受的工作可進入短期板。

## 操作規則

- 只使用本倉庫中已公開、已授權的資料；不要求私人 Memory、原始對話、隱藏推理或本機私人路徑。
- 本 Profile 的跨倉庫公共交換只使用 `accountable-dialogue/change-case-v0`；不要新增平行 continuity schema 或可寫人格狀態。
- 模型可以提出方案、檢查與反例，不能自行作出人類治理決定或把提案說成定案。
- 資源總量或剩餘量沒有工具來源時，一律標為 `not_reported`，不可推測 token budget。
- 先寫失敗測試，再做最小實作；完成前執行 `python -m pytest tests/ -x` 與 `python -m ruff check accountable_dialogue tests`。
- 公開前逐項檢視 staged paths，並再次依 `PUBLIC_BOUNDARY.md` 做人工邊界檢查。
