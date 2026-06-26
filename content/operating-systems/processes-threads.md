# 行程與執行緒

## 核心概念
Process 是資源容器，擁有位址空間、開啟檔案、權限與 PCB；thread 是 CPU 排程的執行單位，通常共享同一 process 的記憶體與檔案。Program 是靜態檔案，process 是執行中的實例。

```
Process
├─ address space / files
└─ threads：PC、registers、stack
```

Context switch 會保存目前執行狀態並載入下一個可執行單位。`fork` 建立新 process，`exec` 用新程式映像取代目前 process。
作業系統題常把「隔離」與「共享」放在一起考：process 隔離能提升保護性，thread 共享能降低溝通成本，但一旦共享資料，就必須面對同步與記憶體可見性。
判斷題目時，先找資源屬於 process 還是 thread，再推導切換與通訊成本。
這能避免把共享記憶體問題誤判成行程隔離問題。

## 解題重點
- Process 間隔離較強，IPC 需 pipe、socket、shared memory 等機制。
- Threads 溝通便宜，但共享資料需要同步。
- 狀態常見為 new、ready、running、blocked、terminated。
- Kernel thread 由 OS 排程；user thread 切換快但可能受 blocking system call 影響。

## 常見陷阱
Thread 不是比較小的 process 而已，重點是共享 address space。多執行緒不保證變快，鎖競爭與 cache coherence 會吃成本。Zombie 是已結束但尚未被 parent 回收狀態，不是仍在執行。

## 練習前檢查
你應能分清 program/process/thread、畫出狀態轉移，並說明 context switch、PCB、fork/exec、IPC、race condition、user/kernel thread 與多核心平行的限制。
