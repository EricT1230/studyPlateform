# CPU 排程

## 核心概念
CPU 排程決定 ready queue 中誰取得 CPU。常見目標包含高 CPU utilization、高 throughput、低 turnaround time、低 response time、低 waiting time 與公平性；不同工作負載會讓目標互相拉扯。

```
ready → running → blocked
   ↑        ↓
   └── preempt / yield
```

Preemptive scheduler 可中斷目前執行者；non-preemptive 則等它阻塞或主動讓出。I/O-bound 工作常短 CPU burst，CPU-bound 工作則長時間計算。
排程不是單純找「最快」演算法，而是在互動性、吞吐、公平與可預測性間取捨。做表格題時，先畫時間軸，再從每個 process 的到達、開始、完成時間推導指標。
若題目允許搶佔，時間軸會在新工作到達、時間片用完或 I/O 阻塞時切段；若不允許搶佔，就等目前工作讓出 CPU。
所有指標都應從同一條時間軸一致計算。

## 解題重點
- FCFS 簡單但可能有 convoy effect。
- SJF/SRTF 對平均等待時間好，但需要預測 burst。
- Round Robin 靠 time quantum 改善互動反應。
- Priority scheduling 要處理 starvation，常用 aging。
- MLFQ 會依行為動態調整優先權。

## 常見陷阱
Quantum 太小會讓 context switch overhead 過高；太大又接近 FCFS。Response time 不是 turnaround time。Priority inversion 是低優先權持鎖阻塞高優先權，可能需要 priority inheritance。多核心排程還要考慮負載平衡與 cache affinity。

## 練習前檢查
你應能手算等待與完成時間、比較 FCFS/SJF/SRTF/RR/priority/MLFQ，並說明 preemption、aging、real-time deadline、throughput 與 fairness 的取捨。
