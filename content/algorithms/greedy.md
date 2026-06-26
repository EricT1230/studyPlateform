# 貪心法

## 核心概念

貪心法每一步做當下看起來最好的選擇，並期待這些局部選擇能組成全域最佳解。它需要 greedy-choice property 與 optimal substructure，不能只靠直覺。常見例子有 activity selection、interval scheduling、Huffman coding、Kruskal、Prim、Dijkstra 與 fractional knapsack。

## 解題重點

先寫出排序或優先規則，再證明它安全。常用證明法包括 exchange argument、cut property 與 loop invariant。例如區間選擇常選最早結束者；MST 題常用 cut property 說明最輕跨邊可以被某棵 MST 接受。

```text
sort by finish time
take activity if start >= last_finish
```

## 常見陷阱

0/1 knapsack 不能直接用 value/weight 貪心；硬幣找零只在特定幣制可靠；set cover 的貪心通常只是近似。Dijkstra 的貪心成立依賴非負權重。

## 練習前檢查

能否構造反例推翻你的規則？能否把任一最佳解交換成含有貪心選擇的最佳解？題目要最佳解還是可接受近似？
