# 堆疊與佇列

## 核心概念

Stack 是 LIFO，最後放入者最先取出；queue 是 FIFO，最早進入者最早離開。兩者可用動態陣列、linked list 或 circular buffer 實作。Deque 支援兩端 push/pop，monotonic stack/deque 則用「維持單調」換取線性時間。

```text
stack: push, pop, top
queue: enqueue, dequeue, front
circular: rear = (rear + 1) mod m
```

## 解題重點

Stack 常用於括號配對、遞迴 call stack、DFS、infix/postfix 轉換與 next greater element。Queue 常用於 BFS 與事件模擬。兩個 stack 可實作 queue，每個元素最多搬移一次，所以操作可攤銷 `Theta(1)`。

## 常見陷阱

Circular queue 只靠 `front == rear` 無法同時區分空與滿，常需 size 或保留一格。BFS 若 visited 標記太晚，可能重複入隊。攤銷 `O(1)` 不等於每一次都 `O(1)`。

## 練習前檢查

題目要的是最近未配對、最早到達，還是當前最大/最小？資料結構是否需要固定容量？空集合操作是否定義清楚？
