# J0 Transport Observability Successor v0

> 狀態：`v0.1-proposed`。此文件只準備更誠實的 transport failure 記錄；它不授權目前不受支援 host 上的新模型呼叫。

## 為何需要 successor

J0 initial probe 的三筆 generation 都只有 `transport_error`。後續只讀診斷已顯示本機 native
runner crash 與不受支援的 Windows 10 build；原始 probe 已完整保留，不能回頭改寫或重跑。

原 runner 另有一個可修正的可觀測性缺口：Python 的 `HTTPError` 是 `URLError` 的子類，舊 transport
會將 HTTP status、網路失敗、非 JSON 與 provider response-contract failure 全部壓成同一個 generic
category。Ollama 的 Generate endpoint 支援 `format: "json"`，而 API error 則以 HTTP status 與 error
payload 表達；因此只靠舊的 generic category 不能判定實際 failure kind。[Ollama Generate API](https://docs.ollama.com/api/generate)
[Ollama API errors](https://docs.ollama.com/api/errors)

## 新的安全觀測契約

未來 J0 external run row 可在既有 `mechanical_status` 外，帶一個可選的 `transport_observation`：

```text
kind: timeout | network_error | http_4xx | http_5xx | http_other | provider_contract_error
http_status: 僅 http_* 時的 100–599 整數
```

它明確**不得**包含：exception text、HTTP error body、headers、base URL、local path、credential、raw prompt
或 raw model output。成功或已完成 semantic comparison 時，此欄位為 `null`。

這不是一個新的 judge score；它只說明為何該列無法進入 judge JSON／label comparison。

## 程序與停止規則

1. 這個 repository 可先用 mock transport 驗證安全分類與無洩漏輸出，但不得在目前 Windows 1903 host
   上送出新的 generation。
2. 只有擁有者選擇官方支援的 host 或完成其他 repository 外的環境決定後，才可另建一個單一、全合成、
   non-semantic compatibility probe。
3. 那個 probe 是新的 successor，不是 initial probe 的 retry；它不下載模型、不改 initial fixture/key、
   不取代兩位外部獨立人類 H1 rater。
4. 即使得到 `http_4xx`／`http_5xx`，也只記錄安全 category，不能以 server error text 或臆測補成模型能力結論。

## 目前未完成的事

- 擁有者尚未選擇升級目前 host、改用另一個支援 host，或停止 local judge 探索；
- 沒有新的 compatibility generation；
- 沒有 Qwen、Llama、H1 或人類 rater 的新增結論。
