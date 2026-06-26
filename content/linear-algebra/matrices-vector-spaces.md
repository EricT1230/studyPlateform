# 矩陣與向量空間

## 核心概念

矩陣乘法需內側維度相同：`(m x n)(n x p)` 得 `m x p`。向量空間重點在 span、linear independence、basis 與 dimension。向量組 linearly independent 表示 `c1v1+...+ckvk=0` 只有全零係數解；basis 是同時能 span 整個空間且獨立的向量組。Subspace 必須包含 zero vector，並對加法與 scalar multiplication 封閉。這些概念其實都在問「哪些方向可被組合出來」以及「表示法是否唯一」。

## 解題重點

Rank 可由 row reduction 的 pivot 數取得，也等於 column space 與 row space 的維度。座標轉換時，若 `P` 的 columns 是 basis `B`，則 standard coordinates 滿足 `[v]_std=P[v]_B`。Projection 題要找目標子空間與正交分量。Row space 與 null space 正交，因為 `Ax=0` 表示 `x` 與每一列內積為零。Diagonalization 則是在找一組由 eigenvectors 組成、讓矩陣作用最簡單的 basis。

## 常見陷阱

非零向量不一定獨立；在 `R^2` 中兩個向量若互為 scalar multiple，只 span 一條線。集合含有不等式或非齊次方程通常不是 subspace。`rank(AB)` 不會超過 `rank(A)` 或 `rank(B)`，但不一定等於兩者乘積。Determinant 非零只適用於方陣的可逆判斷。

## 練習前檢查

矩陣尺寸是否可乘？pivot columns 對應的是原矩陣欄位還是化簡後欄位？要證 subspace 時，zero vector、加法封閉、純量封閉三項是否都過？座標使用的是哪個 basis？若要比較空間，先確認它們位在同一個 ambient space。
