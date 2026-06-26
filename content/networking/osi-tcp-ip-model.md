# OSI 與 TCP/IP 模型

## 核心概念
分層模型用來切開責任。OSI 有七層，TCP/IP 常簡化為應用、傳輸、網際網路、連結。每層只依賴下層服務，並向上層提供抽象；資料往下送時逐層封裝，收端再逐層拆開。

```
App data
→ TCP/UDP segment
→ IP packet
→ Ethernet frame
→ bits
```

典型對應：HTTP/DNS 在應用層，TCP/UDP 在傳輸層，IP/ICMP 在網路層，Ethernet/Wi-Fi 在資料連結層。
分層不是說實作永遠完全分離，而是提供分析問題的座標。遇到故障題時，先問「名稱解析、連線建立、路由、鏈路、實體訊號」是哪一層先失效。

## 解題重點
- Port 是傳輸層用來分辨行程；IP address 是網路層定位主機或介面。
- MAC address 只在同一 link 內有意義，跨 router 會換 frame。
- Router 看 IP 轉送；switch 主要看 MAC；hub 只處理實體訊號。
- Encapsulation 題要看 header 是哪一層加的。

## 常見陷阱
IP 是盡力而為，不保證可靠、順序或不重複；可靠性通常由 TCP 或應用層補。TLS 常被視為介於應用與傳輸之間，不等同於 TCP。DNS 是應用層協定，即使它常用 UDP。

## 練習前檢查
你應能把常見協定放到正確層級、解釋封裝與解封裝、分清 frame/packet/segment，也能說明每層位址、錯誤處理與多工責任的差異。
