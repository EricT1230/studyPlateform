# 離散數學基礎

## 核心概念

離散數學把邏輯、集合、函數、關係與計數放在同一套語言中。命題 `P => Q` 只在 `P` 真且 `Q` 假時為假，常可改寫成 `not P or Q`。集合運算要熟悉交集、聯集、差集、補集與 De Morgan law。函數要區分 domain、codomain、image；有限集合大小也會限制 injective 與 surjective 是否可能。基礎題常不是考計算量，而是考你能否把文字翻成精確符號。

## 解題重點

遇到證明題，先判斷適合直接證明、反證、逆否命題、數學歸納或反例。計數題從乘法原理、組合數、排容原理開始；遞迴題可用展開、遞迴樹或 characteristic equation 觀察成長。關係題要逐一檢查 reflexive、symmetric、antisymmetric、transitive，因為 equivalence relation 與 partial order 的條件不同。每一步最好能說出使用的定義或定理名稱。

## 常見陷阱

`P => Q` 與 converse `Q => P` 不等價。`not forall` 會變成 `exists not`，量詞否定時不能只改最後的述詞。有限集合中，domain 較小不可能 onto 到較大的 codomain，但可能 one-to-one。偏序不要求任兩元素可比較，total order 才要求。

## 練習前檢查

能否寫出每個符號的精確意思？要證明的是全稱、存在還是條件命題？集合或函數是否有限？若使用公式，前提條件是否已滿足？
