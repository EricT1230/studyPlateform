# 同步

## 核心概念
同步處理多個執行緒或行程同時存取共享狀態的問題。Critical section 需要 mutual exclusion，正確解通常還要考慮 progress 與 bounded waiting。Race condition 來自操作交錯導致結果依時序而變。

```
lock → 檢查/修改共享資料 → unlock
```

Mutex 用於互斥；semaphore 可做計數資源或事件排序；monitor 把共享資料與操作封裝，常搭配 condition variable；CAS、TestAndSet 等原子指令是建立鎖與無鎖結構的基礎。
正確同步要同時看 safety 與 liveness：前者避免錯誤交錯，後者避免所有人卡住或某些人永遠等不到。只讓測試偶爾通過，不代表設計正確。
要用不變量思考共享狀態。

## 解題重點
- Producer-consumer 常用 mutex + empty/full semaphores。
- Readers-writers 允許多讀，但寫者需獨佔。
- Deadlock 四條件：互斥、持有並等待、不可搶佔、循環等待。
- 預防是打破條件；避免是保持安全狀態；偵測是事後復原。

## 常見陷阱
Busy waiting 對長等待浪費 CPU，但短臨界區有時可接受。Condition variable 的 wait 通常要放在 while 中重查條件。Deadlock 是停住不動；livelock 是一直動但無進展；starvation 是長期拿不到資源。

## 練習前檢查
你應能寫出基本鎖保護流程、判斷 semaphore 初值，並說明 dining philosophers、Banker's algorithm、priority inversion、ABA 問題與 memory barrier 的用途。
