# 雜湊表

## 核心概念

Hash table 用 hash function 把 key 映射到 bucket，目標是讓查找、插入、刪除在平均或期望下接近 `Theta(1)`。碰撞不可避免，需要 separate chaining 或 open addressing 處理。Load factor `alpha = n / m` 是效能的核心指標。

## 解題重點

Chaining 把同 bucket 的 key 放在串列、陣列或樹中；open addressing 把元素放在表內，透過 probing 找空位。表太滿時要 resize 並 rehash，雖然單次 `O(n)`，但可攤銷。查找時 hash value 相同仍要做 equality check。

```text
index = hash(key) mod m
expected cost ~= O(1 + alpha)
```

## 常見陷阱

以為 hash table 永遠最壞 `O(1)`；惡意碰撞可退化。Open addressing 刪除時不能直接清空 slot，常需 tombstone。Linear probing 容易 primary clustering；key 若可變，插入後改 key 會破壞查找。

## 練習前檢查

key 是否有穩定 equality 與 hash？是否需要排序或 range query？load factor 是否受控？面對外部輸入是否需要 randomized hashing？
