# 堆積與優先佇列

## 核心概念

Binary heap 是 complete binary tree，通常用陣列表示。Min-heap 只保證每個父節點不大於子節點，因此 root 是最小值，但左右子樹之間沒有完整排序。Priority queue 用它支援 `find-min`、`insert`、`extract-min` 等操作。

```text
0-based: left=2i+1, right=2i+2, parent=(i-1)//2
insert / extract-min: O(log n)
build-heap: O(n)
```

## 解題重點

插入後用 sift-up，刪除 root 後把最後元素搬到 root 再 sift-down。Top-k 可維持大小為 k 的 min-heap；k-way merge 維持每條序列目前元素，總時間常是 `Theta(n log k)`。Dijkstra 的 priority queue key 是 tentative distance。

## 常見陷阱

Heap 不是 BST，不能二分查找任意 key。Min-heap 找最大值最壞需看葉節點，通常是 `Theta(n)`。支援 decrease-key 時要知道元素在 heap array 的位置。

## 練習前檢查

你需要反覆取最小/最大，還是只排序一次？是否要 meld 多個 heap？穩定性是否重要？索引公式是否與 0-based/1-based 一致？
