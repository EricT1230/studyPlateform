# HTTP

## 核心概念
HTTP 是 request/response 協定，本身無狀態；登入與購物車等狀態要靠 cookie、session 或 token 補上。一次訊息可分成起始列、headers 與 body；HTTPS 則是 HTTP 跑在 TLS 上，提供機密性、完整性與身分驗證。

```
Client request  →  Method URI Headers Body
Server response ←  Status Headers Body
```

方法語意很重要：GET 偏取得、POST 偏提交或建立、PUT 常用整體替換、DELETE 刪除資源。
實務上 HTTP 題常混合協定語意與瀏覽器行為：伺服器回什麼狀態碼、瀏覽器是否帶 cookie、快取能不能重用，會一起影響使用者看到的結果。
因此要同時看請求與回應。

## 解題重點
- 狀態碼分類：2xx 成功、3xx 重新導向、4xx 用戶端錯、5xx 伺服器錯。
- Safe 不應改變伺服器狀態；idempotent 表示重複執行最終效果相同。
- `Content-Type` 說明 body 格式；`Cache-Control` 控制快取策略。
- HTTP/2 多工串流與壓縮標頭；HTTP/3 基於 QUIC。

## 常見陷阱
401 偏未驗證，403 偏已知身分但無權限。`no-cache` 不是禁止儲存，而是使用前要再驗證；`no-store` 才是不保存。CORS 是瀏覽器安全機制，不是伺服器之間的通用防火牆。

## 練習前檢查
你應能判斷方法語意、選合適狀態碼、讀懂常見 headers，並說明 REST 資源導向、cookie 狀態維持、TLS 保護與 HTTP/1.1 keep-alive 的效益。
