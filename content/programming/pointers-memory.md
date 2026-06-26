# 指標與記憶體

## 核心概念

指標儲存位址；`&x` 取得位址，`*p` 取用該位址上的物件。指標運算以 pointed type 的大小為單位，不是單純加 byte。動態記憶體由 `malloc/calloc/realloc` 取得，最後必須由負責 ownership 的一方 `free`。

```c
int a[10];
int *p = &a[2];
p + 3; // points to a[5]
```

## 解題重點

`const int *p` 表示不能透過 p 改 pointed int；`int * const p` 表示 p 不能改指向。`realloc` 可能失敗，安全寫法是先存到暫時指標。若函式要改變呼叫端的指標值，參數通常要用 pointer to pointer。

```c
void *tmp = realloc(p, n);
if (tmp) p = tmp;
```

## 常見陷阱

Dereference `NULL`、one-past 指標或已 `free` 的指標都是 undefined behavior。Double free 會破壞 allocator 狀態。回傳區域變數位址會形成 dangling pointer。Strict aliasing 規則也可能讓不合法型別轉換出錯。

## 練習前檢查

這塊記憶體誰配置、誰釋放？指標目前是否仍指向有效物件？每次 `free` 前是否還需要保存 next？轉型後讀寫是否符合 C 的 aliasing 與 alignment 要求？
