# J0 Judge Calibration 直接啟動嘗試（2026-07-16）

> 狀態：`preflight_launch_failure`。這不是模型 probe 結果，也不是 retry 後的模型結果。

## 發生了什麼

在 J0 harness 與 preparation change case 已推到 `main` 後，直接以
`python scripts/run_judge_calibration.py --output-dir ...` 啟動固定 probe。Python 在載入
runner 時找不到 `accountable_dialogue` package，因此在進入 `main()` 前以
`ModuleNotFoundError` 停止。

## 可確認的邊界

- 零次 Ollama generation；
- 沒有 Qwen 或 Llama output、timeout 或 calibration verdict；
- 沒有下載、pull、改動本機模型或網路 endpoint；
- 因 runner 尚未建構 client 和 output directory，沒有 J0 raw output 需要公開或保存。

這是一個 CLI import-path 缺口，不是對已安裝模型能力、語義判斷或資源的觀察。

## 後續處置

以一個直接執行 `--help` 的 subprocess regression test 固定此入口，再讓 runner 將 repository
root 加入自身的 import path。修正、測試、commit 和 push 完成後，才可以開始尚未消耗的三次固定
local-only probe；不得把本次 preflight failure 算成模型 retry。
