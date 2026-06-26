# 鏈結串列

## 核心概念

Linked list 由節點與指標串起來，節點通常含有 value 與 next；doubly linked list 再加 prev。它不保證連續記憶體，因此無法像陣列一樣 `O(1)` 隨機存取，但若已握有節點或前一個節點，插入與刪除可只改幾個指標。

```c
struct Node {
  int value;
  struct Node *next;
};
```

## 解題重點

Singly linked list 查第 i 個元素要從 head 走，時間 `O(n)`。若用 linked list 實作 queue，保留 head 與 tail 才能讓 enqueue/dequeue 都是 `O(1)`。刪除節點時要先保存 next，再釋放目前節點。

## 常見陷阱

只保留 head 卻想在尾端 `O(1)` 插入。刪除第一個節點、最後一個節點與空串列常有邊界錯。C 中 `free(node)` 後再讀 `node->next` 是 dangling pointer 問題。

## 練習前檢查

是否需要快速隨機存取？是否經常在中間插刪？有沒有 dummy head 能簡化邊界？每次改指標後，串列是否仍可從 head 走到尾？
