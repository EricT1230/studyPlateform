# I/O 與儲存

## 核心概念
OS 透過 driver 把一般 I/O 介面轉成特定硬體命令。Polling 由 CPU 反覆查狀態；interrupt 讓裝置完成或就緒時通知 CPU；DMA 讓控制器直接在裝置與記憶體間搬資料，CPU 只設定描述與處理完成事件。

```
程式 → system call → driver → controller → device
```

Latency 是單次請求等待時間，throughput 是單位時間完成量。Buffering 可吸收速率差、合併小 I/O 與支援非同步。
解題時先問資料路徑由誰搬：CPU 自己搬、裝置中斷通知、還是 DMA 背景搬運。再看裝置特性，因為 HDD、SSD、網卡的瓶頸與最佳排程策略不同。
同一個演算法在不同裝置上可能效果相反。

## 解題重點
- MMIO 把裝置暫存器映射到位址空間，driver 用 load/store 存取。
- HDD 排程關注 seek 與旋轉延遲；SCAN 類演算法減少磁頭來回。
- SSD 由 FTL 管理 LBA 到 flash 的映射、wear leveling 與 garbage collection。
- TRIM 告訴 SSD 哪些邏輯區塊已不再使用。

## 常見陷阱
Buffer 不等於 durable，斷電保證要看 flush、barrier、fsync 或硬體保護。RAID 1/5 提高可用性，不是離線備份。SSD 不能任意原地覆寫，需要 erase-before-write，隨機小寫可能放大寫入成本。

## 練習前檢查
你應能比較 polling、interrupt、DMA，說明 driver、completion queue、blocking/non-blocking/async I/O，並辨識 HDD、SSD、RAID、TRIM、write-back cache 的效能與可靠性取捨。
