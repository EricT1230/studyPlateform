# 計算機架構基礎

## 核心概念
計算機架構先分清兩層：ISA 是軟體看得見的契約，包含指令、暫存器、位址模式與例外語意；microarchitecture 是實作方式，例如管線、ALU、cache 與分支預測。同一 ISA 可有不同效能、功耗與成本的實作。

```
程式 → ISA → 內部實作 → 記憶體 / I/O
```

效能常用 `CPU time = 指令數 × CPI ÷ clock rate`。記憶體階層越靠近 CPU 越快但越小；越往外容量越大但延遲越高。
讀題時先判斷它在問「規格契約」、「硬體實作」還是「效能模型」，可避免把不同層次混在一起。

## 解題重點
- 問「可見行為」多半是 ISA；問「如何加速」多半是 microarchitecture。
- 算時間時先統一單位：GHz 是每秒十億 cycle。
- Amdahl's Law 要看「可加速比例」，不是只看局部快幾倍。
- cache 題常從時間局部性、空間局部性判斷。

## 常見陷阱
Pipeline 主要提高長串指令 throughput，不保證單一指令 latency 變短。CPI 低不一定代表執行快，還要看指令數與時脈。Interrupt 可減少 polling 浪費，但仍有保存狀態與 handler 成本。

## 練習前檢查
你應能說明 ISA 與 microarchitecture 差異、代入 CPU time 公式、判斷記憶體階層方向，並解釋 interrupt、locality、Amdahl's Law 的基本取捨。
