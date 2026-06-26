# 圖演算法

## 核心概念

圖由頂點與邊組成，可用 adjacency list 或 matrix 表示。List 適合 sparse graph，遍歷常是 `O(V + E)`；matrix 查 `(u,v)` 是否有邊是 `O(1)`，但空間是 `O(V^2)`。BFS 解無權重最短路，DFS 支援 cycle、拓撲排序、SCC 與 low-link 類問題。

## 解題重點

先確認有向或無向、是否有權重、是否可能有負邊。DAG 可拓撲排序後做 DP；Dijkstra 要非負權重；Bellman-Ford 可偵測可達負環；Kruskal/Prim 解 MST；max-flow 要看 residual graph 與 augmenting path。

```text
BFS/DFS on list: O(V + E)
Floyd-Warshall: O(V^3)
```

## 常見陷阱

把 MST 當 shortest path。Directed cycle 的 DFS 判斷要看 recursion stack，不只是 visited。Topological sort 只適用 DAG；Kahn 處理不到所有點通常代表有 directed cycle。

## 練習前檢查

題目要求路徑、連通性、排序、切割還是流量？圖的表示法是否影響時間？邊權條件是否允許使用你選的演算法？
