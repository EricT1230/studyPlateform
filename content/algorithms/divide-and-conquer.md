# 分治法

## 核心概念

分治法包含三步：divide 拆成較小子問題，conquer 遞迴解子問題，combine 合併結果。Binary search、merge sort、quicksort、quickselect、inversion count、closest pair、Karatsuba 與 Strassen 都屬於這個思路。

```text
T(n)=aT(n/b)+f(n)
merge sort: T(n)=2T(n/2)+Theta(n)
```

## 解題重點

判斷子問題是否獨立、大小是否穩定縮小、合併成本是多少。遞迴樹可快速估每層成本；Master theorem 適合規則的 `aT(n/b)+f(n)`。正確性通常用 induction：假設子問題正確，再證明 combine 不破壞答案。

## 常見陷阱

沒有 base case 會無限遞迴。Quicksort 平均快，但 pivot 極端時可退化到 `Theta(n^2)`。Merge sort 通常穩定但需要額外 `Theta(n)` 空間；heapsort 空間省但通常不穩定。

## 練習前檢查

每次是否真的縮小問題？合併步驟是否漏掉跨左右兩半的答案？遞迴式的 `f(n)` 是分割成本、合併成本，還是兩者合計？
