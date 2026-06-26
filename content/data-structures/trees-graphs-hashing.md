# 樹、圖與雜湊整合

## 核心概念

樹、圖與雜湊常在同一題中比較取捨。BST 維持 key 的順序，平衡後查找與更新可達 `O(log n)`；heap 只保證優先順序；trie 按字元路徑查 prefix；graph 用邊描述關係；hash table 用 key 直接定位 bucket。

## 解題重點

若需要 range query 或依序輸出，balanced search tree 通常比 hash table 合適。若只做 exact lookup，hash table 平均較快。Sparse graph 適合 adjacency list；dense graph 或常查某邊是否存在時，可考慮 adjacency matrix。DSU 適合無向連通性與 Kruskal，但不表示有向鄰接。

```text
BST inorder => sorted keys
matrix[u][v] => O(1) edge check
hash expected lookup => O(1)
```

## 常見陷阱

把 heap 當排序好的樹。用 hash table 解需要順序的題。對 sparse graph 使用 matrix 造成 `O(V^2)` 空間浪費。BST 若未平衡，排序插入會退化成 linked list。

## 練習前檢查

操作需要順序、範圍、prefix、連通性還是 exact lookup？資料是稀疏還是稠密？最壞情況是否重要？
