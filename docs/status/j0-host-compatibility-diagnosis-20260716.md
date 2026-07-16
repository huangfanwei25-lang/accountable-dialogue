# J0 Host／Runtime Compatibility 診斷（2026-07-16）

> 狀態：`host_runtime_compatibility_failure_candidate`。這是對初始 J0 transport result 的後續**只讀**診斷；沒有新增 generation、下載、restart 或模型檔變更。

## 新增的可檢查觀察

初始 probe 後，本機 loopback service 仍可回應 `/api/version`、`/api/tags` 與 `/api/ps`；CLI 與服務都回報
Ollama `0.32.0`，三個模型仍列在 catalog 中，且沒有模型保持載入。這排除了「服務完全不可達」或
「目標名稱一開始就不在 catalog」兩種較粗略的解釋。

Windows Application Error 與 Windows Error Reporting 在三次 J0 呼叫的時間附近各留下三筆相對應事件：
`llama-server.exe` 在 `ucrtbase.dll` 以 `0xc0000409` 停止。這表示生成請求期間的本機 native runner
發生 crash；它不是一個模型產生的 judge verdict。

本機系統為 Windows 10 Home `10.0.18362`（1903）。Ollama 目前的 Windows 文件要求 Windows 10
22H2 或更新版本；因此這個 host build 不在公開支援範圍內。[Ollama Windows system requirements](https://docs.ollama.com/windows)

## 可做的推論與不可做的推論

最強且仍然有界的推論是：本輪失敗是**不受支援 host build 上的 runtime／compatibility failure candidate**，
足以停止任何進一步的本機 J0 generation。Application event 的 crash 落點與不受支援的 OS build 並不能
單獨證明唯一 root cause；例如它不證明 `ucrtbase.dll` 本身、某個模型、prompt 或 Ollama 版本就是唯一原因。

因此不能將這次結果寫成：

- Qwen 或 Llama 不會做 rubric judge；
- `format: "json"` 是錯誤來源（它是 Ollama Generate API 支援的 format）；
- 小模型不誠實、沒有知識邊界或沒有自我認知；
- 兩位外部人類 H1 盲評的替代證據。

## 後續需要的人類決定

系統更新、改用另一台支援的 host 或改變計算環境都是 repository 外、可能影響使用者工作環境的行動，
不由 runner 或助理默默執行。下一步需由擁有者選擇：

1. 將目前 host 升級到官方支援的 Windows 10 22H2 或更新版本；
2. 在另一個已支援的本機／受控 host 執行新的、全合成 J0 successor；或
3. 停止本機小模型 judge 探索，維持兩位外部獨立人類為唯一正式 H1 評審軌道。

不應藉由下載另一個模型或重試原始三次呼叫來繞過這個 compatibility boundary。
