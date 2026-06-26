# 排序

## 核心概念

排序題通常比較四件事：時間複雜度、空間、穩定性與是否基於比較。Comparison sort 的一般下界是 `Omega(n log n)`，因為必須區分 `n!` 種可能順序。Merge sort 穩定且 `Theta(n log n)`，但常需額外空間；heapsort 最壞 `Theta(n log n)` 且空間省；quicksort 平均快但最壞可能 `Theta(n^2)`。

## 解題重點

遇到「穩定」要看相同 key 的相對順序是否保留。遇到「in-place」要看額外空間，而不是輸入陣列本身。若資料是整數且範圍小，可考慮 counting/radix 類非比較排序，突破比較排序下界。

```text
merge sort: T(n)=2T(n/2)+Theta(n)
comparison lower bound: log2(n!) = Omega(n log n)
```

## 常見陷阱

把 average、expected 與 worst-case 混用。Selection sort 通常不穩定；quicksort 也通常不穩定。Heap 只保證父子順序，不保證整個陣列已排序。

## 練習前檢查

題目是否要求穩定？資料是否已有序或近乎有序？比較成本是否昂貴？答案要 worst-case 還是平均情況？
