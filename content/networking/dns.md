# DNS

## 核心概念
DNS 是分散式名稱系統，把容易記的人類名稱對到 IP 或其他服務資訊。階層由 root、TLD、權威名稱伺服器一路委派；用戶端通常問 recursive resolver，resolver 再用 iterative 查詢逐層取得答案。

```
client → resolver → root → TLD → authoritative
```

常見紀錄包含 A/AAAA、CNAME、MX、NS、TXT、PTR、SOA。TTL 決定快取能保留多久，是查詢量與變更速度之間的取捨。
解析不是每次都從 root 重新開始；resolver 與作業系統、瀏覽器都可能快取結果。排查問題時，要同時思考權威資料是否正確，以及沿途快取是否仍保留舊答案。
也要確認查的是正確 record type。

## 解題重點
- 一般查詢多用 UDP/53；大型回應、截斷重試或 zone transfer 會用 TCP。
- CNAME 是別名，MX 指郵件伺服器，PTR 做反查。
- Root 不存所有網域，只指引下一層。
- 短 TTL 變更快，但快取命中率下降。

## 常見陷阱
DNSSEC 提供簽章驗證與完整性，不負責加密查詢內容；DoH/DoT 才是加密傳輸。Cache poisoning 是讓解析器記住假答案。Anycast 不是廣播給所有節點，而是同一 IP 由多地節點宣告。

## 練習前檢查
你應能畫出解析流程、辨認常見 record、說明 recursive 與 iterative 差異，並理解 TTL、negative caching、amplification attack 與 DNSSEC/DoH/DoT 的不同安全目標。
