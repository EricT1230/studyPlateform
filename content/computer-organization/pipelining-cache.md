# 管線與快取 (Pipeline & Cache)

## 管線：像洗衣店流水線

一條指令分成幾個階段。與其一條做完才做下一條，不如**讓不同指令的不同階段同時進行**，提高吞吐。

生活類比：洗衣店有「洗→烘→摺」三台機器。第一批在烘時，第二批就能開始洗——機器不閒置。

五階段：IF（取指）→ ID（解碼）→ EX（執行）→ MEM（存取記憶體）→ WB（寫回）。

```
週期:   1    2    3    4    5    6    7
I1:    IF   ID   EX   MEM  WB
I2:         IF   ID   EX   MEM  WB
I3:              IF   ID   EX   MEM  WB
```

理想下，填滿後**每個週期完成一條指令**。但注意：單一指令的總時間（latency）沒變短，變好的是**吞吐 (throughput)**。

## 管線的三種危障 (hazard)

讓管線無法順跑、要插入 stall 的狀況：
- **結構危障 (structural)**：兩條指令同時搶同一個硬體資源。
- **資料危障 (data)**：後一條要用前一條還沒算好的結果（RAW）。
- **控制危障 (control)**：遇到分支，還不知道下一條該抓哪裡。

解法：
- **forwarding（資料前送）**：算好的結果直接送給需要的階段，省去多數 RAW stall。但 **load-use**（load 完馬上用）仍可能停一拍。
- **分支預測**：先猜分支方向；猜錯要把錯抓的指令清掉 (flush)，有懲罰。

## 快取：把常用資料放近一點

靠**局部性**，把熱資料放在快層。位址被拆成三段來查快取：

```
記憶體位址 = [   tag   |  index  |  offset  ]
                ↑          ↑          ↑
            驗證命中    挑哪個 set    block 內第幾個 byte
```

- **offset**：定位 block（cache line）內的位置。
- **index**：定位放在哪一個 set / line。
- **tag**：比對確認「這格存的真的是我要的位址」。

## 平均存取時間 AMAT

```
AMAT = 命中時間 + 失誤率 × 失誤懲罰
       hit time + miss rate × miss penalty
```

實例：hit time 1 cycle、miss rate 5%、miss penalty 100 cycles
→ AMAT = 1 + 0.05 × 100 = 6 cycles。

## 三種 cache miss（3C）

- **強制 miss (compulsory)**：第一次存取，本來就不在 → 不可避免。
- **容量 miss (capacity)**：快取太小，裝不下工作集。
- **衝突 miss (conflict)**：映射方式讓多個 block 搶同一格。

提高**關聯度 (associativity)** 主要減少**衝突** miss，但消不掉強制 miss。

## 常見誤解

- 管線提高**吞吐**，不縮短**單一指令延遲**。
- 提高 associativity 減 conflict miss，**不會消除首次 (compulsory) miss**。
- **write-through vs write-back** 講的是「何時寫到下一層」；**write-allocate** 講的是「write miss 時要不要先把該 block 載入快取」——別混。

## 解題時的判斷（效能題的鐵則）

1. 先算**理想值**（管線滿載、全命中）。
2. 再**逐項加回**成本：stall、miss penalty、flush。
3. 給比例時，換算成「每指令平均成本」再加總。
4. 這樣比憑直覺猜可靠得多。
