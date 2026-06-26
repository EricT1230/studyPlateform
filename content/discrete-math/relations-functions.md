# 關係與函數

## 核心概念

Relation 是集合上的 ordered pairs。Reflexive 要求每個 `(a,a)` 都在關係中；symmetric 要求 `(a,b)` 推出 `(b,a)`；transitive 要求 `(a,b)` 與 `(b,c)` 推出 `(a,c)`；antisymmetric 則是雙向成立時必有 `a=b`。Equivalence relation 由 reflexive、symmetric、transitive 組成；partial order 由 reflexive、antisymmetric、transitive 組成。前者把元素分群，後者描述「不一定全可比較」的順序。

## 解題重點

函數題先分清 domain、codomain 與 image。Injective 表示不同輸入不同輸出；surjective 表示 codomain 全被覆蓋；bijective 才有 two-sided inverse。有限集合中，若 `|A|=|B|`，injective 與 surjective 可互推。函數合成要注意順序：`g o f` 是先做 `f` 再做 `g`。計算函數數量時，每個 domain 元素都要選 codomain 目標；若要求 injective，則後面的選擇會被前面用掉。

## 常見陷阱

Symmetric 與 antisymmetric 不是互斥否定；某些關係可以同時滿足。Partial order 不要求每兩個元素可比較，total order 才要求。Equivalence classes 會形成 partition，但不是排序。Transitive closure 是包含原關係的最小 transitive relation，不是任意補邊。Modulo 關係常依餘數分成等價類，subset 關係則是偏序的典型例子。

## 練習前檢查

先列出要檢查的 pair 或用定義做一般證明。函數是否真的對每個輸入只有一個輸出？codomain 是否被全數覆蓋？Hasse diagram 是否省略了 self-loop 與可由 transitivity 推出的邊？若答案靠集合大小推論，先確認集合是有限的。
