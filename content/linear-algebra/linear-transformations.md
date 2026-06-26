# 線性變換

## 核心概念

Linear transformation 保留加法與純量乘法：`T(u+v)=T(u)+T(v)`、`T(cu)=cT(u)`，等價於 `T(au+bv)=aT(u)+bT(v)`。因此必有 `T(0)=0`。對 `T: R^n -> R^m`，standard matrix 的第 `j` 欄是 `T(e_j)`。Kernel 是 `{x | T(x)=0}`，image/range 是所有可能輸出。幾何上，線性變換可拉伸、旋轉、投影或剪切，但不會把原點平移走。

## 解題重點

判斷 injective 可看 kernel 是否只有 zero vector；判斷 surjective 到 `R^m` 可看 rank 是否為 `m`。Rank-nullity theorem 是 `dim(domain)=rank+nullity`。Composition 的矩陣順序要反過來讀：若 `T(x)=Ax`、`S(y)=By`，則 `S o T` 的矩陣是 `BA`。換基時，basis vectors 作為 columns 的矩陣 `P` 滿足 `v=P[v]_B`。同一個 operator 在不同 basis 下會得到 similar matrices，但描述的是同一個線性作用。若子空間在作用後仍留在自身內，就稱為 invariant subspace，可把問題縮小到該子空間研究。

## 常見陷阱

`T(x)=Ax+b` 在 `b != 0` 時通常是 affine，不是 linear，因為 `T(0) != 0`。矩陣 entries 會隨 basis 改變，但 rank 是變換本身的性質。Orthogonal matrix 保留長度與 inner product，不代表每個座標不變。Functional 的輸出是 scalar，isomorphism 則必須同時 linear 且 bijective。

## 練習前檢查

先確認 domain 與 codomain 維度。是否檢查了 `T(0)=0`？矩陣乘法順序是否符合「先右後左」？injective、surjective 的 rank 條件是否對應到正確空間維度？若題目談 quotient space，還要確認代表元選擇不影響輸出。幾何圖像可輔助判斷，但最後仍要回到線性條件。輸入輸出空間不同時，別亂用 determinant。
