# 數位邏輯

## 核心概念
數位邏輯分為組合邏輯與循序邏輯。組合邏輯輸出只由目前輸入決定，例如 mux、decoder、adder；循序邏輯有狀態，靠 latch 或 flip-flop 在 clock 控制下保存資訊。

```
輸入 → 組合邏輯 → D flip-flop → 狀態
              ↑             ↓
              └── next-state ┘
```

同步電路的速度受 critical path 限制：clock-to-Q、組合邏輯延遲、setup time 與 clock skew 都要放進同一個 clock period。
練習時把「功能正確」與「時序安全」分開看：布林式正確只代表穩態輸出對，若資料在 clock edge 前後不穩，仍可能造成錯誤取樣。
因此遇到電路題，可先解出邏輯功能，再檢查最慢路徑、暫存器邊界與非同步輸入是否被妥善處理。

## 解題重點
- 真值表、布林式、K-map 與邏輯閘可互相轉換。
- Latch 是 level-sensitive；flip-flop 多為 edge-triggered。
- Moore 輸出只看狀態；Mealy 輸出可同時看狀態與輸入。
- Ripple-carry 慢在 carry 逐位傳遞；carry-lookahead 用 generate/propagate 加速。

## 常見陷阱
Combinational hazard 是延遲不一致造成的短暫 glitch，不一定改變穩態答案。跨 clock domain 取樣可能 metastability，兩級 synchronizer 只能降低機率。Tri-state bus 同時只能有一個 driver 主動驅動。

## 練習前檢查
你應能辨識組合與循序電路、畫出簡單 FSM、檢查 setup/hold 觀念，並說明 static hazard、Gray code、one-hot encoding 與 clock gating 的基本風險。
