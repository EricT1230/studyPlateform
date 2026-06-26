# 管線與快取

## 核心概念
Pipeline 把指令拆成多個階段並重疊執行，目標是提高穩定狀態下的 throughput。常見五階段可想成：

```
IF → ID → EX → MEM → WB
```

Cache 則利用 locality 把常用資料放在較快層級。位址通常拆成 `tag | index | block offset`；offset 找 block 內位置，index 找 set 或 line，tag 驗證是否命中。
這兩個主題都在處理「平均情況如何變快」：管線靠重疊工作，cache 靠大多數存取命中快層級；但 hazard、miss 與預測錯誤會把理想值拉回現實。
分析效能時，先建立理想值，再逐一加回 stall、miss penalty 與 flush 成本，答案會比憑直覺判斷可靠。
若題目給比例，通常要換成每指令平均成本，務必小心。

## 解題重點
- Hazard 分三類：structural 資源衝突、data 相依、control 分支方向未定。
- Forwarding 可減少 RAW stall，但 load-use 仍可能停一拍。
- `AMAT = hit time + miss rate × miss penalty`。
- Miss 類型：compulsory 首次、capacity 容量不足、conflict 映射競爭。

## 常見陷阱
提高 associativity 主要減少 conflict miss，不會消除首次 miss。Direct-mapped 不是容量最小，而是每個 block 位置固定。Write-through 與 write-back 是寫入下一層時機；write-allocate 則是 write miss 時是否載入 cache。

## 練習前檢查
你應能算平均 CPI、分解 cache 位址、判斷分支預測錯誤成本，並說明 coherence、store buffer、prefetch 與 non-blocking cache 對效能與一致性的影響。
