# 進階樹結構

## 核心概念

進階樹的共同目標是用額外 invariant 換取可預測的查詢或更新成本。AVL 與 red-black tree 讓 BST 高度維持 `O(log n)`；B-tree/B+ tree 為磁碟或索引減少 I/O；trie 依字元走訪；segment tree 與 Fenwick tree 支援區間或 prefix 查詢。

## 解題重點

選資料結構前先看操作：exact lookup、range query、prefix search、order statistic 或版本查詢。AVL 查詢較緊，red-black 更新較平衡；B+ tree 的資料多在 leaf，適合 range scan；Fenwick 的 `lowbit(i)` 管一段 suffix-like prefix 區間。

```text
Fenwick: tree[i] covers i-lowbit(i)+1 .. i
Segment tree query/update: O(log n)
```

## 常見陷阱

旋轉後忘記更新高度、顏色或 subtree size。Trie 的時間常看字串長度 `L`，不是元素數 `n`。Lazy propagation 標記若沒有下推，區間更新與查詢容易錯。

## 練習前檢查

需要維持排序嗎？查詢是單點、範圍還是前綴？資料是否在外部儲存？更新頻率是否足以影響結構選擇？
