# 回溯搜尋

## 核心概念

回溯把解空間想成一棵「選擇樹」：每一層做一個決定，若目前部分解已不可能成功，就立刻剪枝並退回上一層。典型流程是選擇、遞迴探索、取消選擇，常見於排列、組合、N 皇后、數獨、Hamiltonian path 與 exact cover。

```text
search(state):
  if complete(state): record
  for choice in candidates(state):
    if valid(choice):
      apply(choice); search(state); undo(choice)
```

## 解題重點

先定義 state、候選選擇、終止條件與合法性檢查。若題目有重複元素，通常要排序並用 `start index` 或「同層跳過相同值」避免重複答案。複雜度常是指數級，例如 subsets 是 `Theta(2^n)`，permutations 是 `Theta(n!)`；剪枝只能降低實測分支，不代表變成多項式。

## 常見陷阱

忘記 undo 會污染其他分支。把 BFS、Dijkstra、A* 與一般回溯混在一起時，要分清楚是否有代價、heuristic 是否 admissible，以及是否需要 visited。

## 練習前檢查

能否說出每層在選什麼？部分解何時必敗？答案是否允許重複順序？最壞情況是否仍需探索大量分支？
