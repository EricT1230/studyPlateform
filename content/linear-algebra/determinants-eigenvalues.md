# 行列式與特徵值

## 核心概念

Determinant 只定義在 square matrix 上，衡量線性變換的有向體積縮放。`det(A) != 0` 等價於 `A` 可逆、rank 滿、columns 線性獨立。Triangular matrix 的 determinant 是主對角線乘積；交換兩列會變號，整個 `n x n` 矩陣乘以 `c` 會使 determinant 變成 `c^n det(A)`。Eigenpair 滿足 `Av=lambda v` 且 `v != 0`，意思是方向不變，只被縮放。行列式符號也可反映 orientation 是否反轉。

## 解題重點

求 eigenvalues 通常先算 characteristic polynomial `det(lambda I-A)`，再解其根。Diagonal matrix 的 eigenvalues 就是對角線元素；trace 等於 eigenvalues 總和，determinant 等於 eigenvalues 乘積（含重數）。Diagonalization 的關鍵是是否有足夠多 linearly independent eigenvectors。若矩陣可寫成 `A=PDP^{-1}`，則高次方、遞迴與穩定性問題都可轉成對角線上的純量問題。Cofactor expansion 適合有很多零的列或欄，否則列運算通常更有效。

## 常見陷阱

`det(A+B)` 一般不等於 `det(A)+det(B)`，但 `det(AB)=det(A)det(B)`。`0` 是 eigenvalue 代表矩陣 singular。Algebraic multiplicity 不保證等於 geometric multiplicity；後者不足時不可 diagonalize。Real symmetric matrix 的 eigenvalues 為 real，但不一定全為正；positive definite 才要求全部大於零。

## 練習前檢查

矩陣是否為 square？row operation 對 determinant 的影響是否被記錄？eigenvector 是否非零？若宣稱可 diagonalize，是否已找到一組 basis 大小的 eigenvectors？相似矩陣共享 characteristic polynomial，但 eigenvectors 需依 basis 轉換。若討論極限，先看最大特徵值絕對值。代入前也要確認多項式定義方向。
