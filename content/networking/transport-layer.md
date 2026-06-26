# 傳輸層

## 核心概念
傳輸層負責端到端的 process 多工。UDP 是 datagram 服務，標頭小、無連線、無可靠保證；TCP 是連線導向的可靠 byte stream，提供排序、重傳、流量控制與壅塞控制。

```
應用資料 → TCP/UDP + port → IP
TCP 建連：SYN → SYN-ACK → ACK
```

TCP 以 sequence number 與 ACK 偵測遺失與重複；receive window 保護接收端，congestion window 探測網路可承受量。
看傳輸層題時先分辨「端點能力」與「網路狀況」：前者影響流量控制，後者影響壅塞控制。可靠性、延遲與開銷通常無法同時最佳化。
即時服務常選擇接受少量遺失，換取穩定延遲與較少排隊。
批次傳輸則通常更重視完整與順序。

## 解題重點
- Flow control 看接收端 buffer；congestion control 看網路壅塞。
- Slow start 約每 RTT 指數成長；AIMD 在壅塞避免中加法增、乘法減。
- Fast retransmit 常由多個 duplicate ACK 觸發。
- UDP 適合低延遲或應用自訂可靠性的場景。

## 常見陷阱
UDP 有 checksum，但不代表會自動重傳。TCP 四向關閉是因為兩個方向各自結束。TIME_WAIT 是為了處理最後 ACK 與舊封包殘留。Nagle 可減少小封包，但可能增加互動延遲。

## 練習前檢查
你應能比較 TCP/UDP、畫出建立與關閉流程、解釋 ports、checksum、rwnd/cwnd、window scaling、SYN flood、head-of-line blocking 與 QUIC 為何改用 UDP。
