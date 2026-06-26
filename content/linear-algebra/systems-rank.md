# 線性系統與秩

## 核心概念

線性方程組 `Ax=b` 有解稱為 consistent；無解稱為 inconsistent。Augmented matrix `[A|b]` 把係數矩陣與右側向量合併，用 row operations 解題。Homogeneous system `Ax=0` 一定有 zero solution。Rank 是 pivot 數，也可理解為 column space 的維度。解集合的形狀由特解加上 null space 決定，因此 rank 同時控制限制數量與自由度。

## 解題重點

Rouche-Capelli theorem 給出一致性條件：`rank(A)=rank([A|b])`。若一致且未知數數量為 `n`、rank 為 `r`，free variables 有 `n-r` 個；沒有 free variable 時唯一解，有 free variable 時通常無限多解。若 `A` 是可逆 square matrix，解為 `x=A^{-1}b`。幾何上，`Ax=b` 有解等價於 `b` 在 `A` 的 column space 中。Rectangular 或 rank-deficient 時，常改問 least squares 或最小 norm 解。SVD 觀點下，rank 是非零 singular values 的個數。

## 常見陷阱

Elementary row operations 不改變 solution set，但 column operations 通常會改變原方程意義。Full column rank 表示 columns independent 與 `Ax=0` 只有 trivial solution；full row rank 表示 rows independent，不必然是 square。Least squares 的 normal equations 是 `A^T A x=A^T b`，不是原系統必有精確解。`rank(A)=rank(A^T)`，但 row space 與 column space 位在不同環境時不能混為一談。

## 練習前檢查

先數未知數、方程數與 pivot 數。化簡後是否出現 `0=nonzero` 的矛盾列？free variables 有幾個？討論數值解時，condition number 是否可能放大誤差？若用 pseudoinverse，題目要的是精確解、least-squares 解，還是最小 norm 解？寫參數解時，每個自由變數都要保留，不要把一組特例誤當完整解。最後代回原式檢查。
