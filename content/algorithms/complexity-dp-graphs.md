# 複雜度、動態規劃與圖

## 核心概念

複雜度分析先抓輸入規模與主導項；`3n + 10` 屬於 `Theta(n)`，遞迴式則看每層成本與層數。動態規劃需要最佳子結構與重疊子問題，把大問題拆成可重用的狀態。圖演算法則高度依賴表示法：adjacency list 常見時間是 `O(V + E)`。

```text
T(n)=2T(n/2)+Theta(n) => Theta(n log n)
dp[i][w] = max(skip, take)
```

## 解題重點

先分清 worst-case、expected、amortized 與 tight bound。DP 題要寫清楚 `dp` 的意義、轉移、初始化與計算順序；DAG shortest path 可用拓撲序做 relaxation。無權重最短路用 BFS，非負權重常用 Dijkstra，可能有負邊時才考慮 Bellman-Ford。

## 常見陷阱

把 `O(n^2)` 當成 `Theta(n)` 的替代答案不精準。0/1 背包不可把同一物品重複拿。Dijkstra 不適合負權重邊；MST 的 Kruskal/Prim 解的是連通成本，不是最短路。

## 練習前檢查

輸入是陣列、表格還是圖？狀態是否唯一且可重用？圖是否有權重、負邊或 cycle？答案要求上界還是 tight bound？
