# C 語言基礎

## 核心概念

C 接近硬體，型別、位址、物件生命週期與未定義行為都要清楚。陣列使用 0-based indexing；字串是以 `'\0'` 結尾的 `char` 陣列；函式參數是 pass-by-value，若要讓函式修改呼叫端變數，必須傳入位址。

```c
int a[5];      // valid index: 0..4
char s[] = "cat"; // sizeof(s) == 4
void f(int *x) { *x = 10; }
```

## 解題重點

`sizeof(array)` 在同一 scope 取得整個陣列大小，但陣列作為參數時會退化成 pointer。`static` 區域變數有 static storage duration，值會跨呼叫保留。`struct` 可能因 alignment 產生 padding，所以 `sizeof(struct)` 不一定等於欄位大小總和。

## 常見陷阱

寫入 string literal 是 undefined behavior。Signed integer overflow 也是 undefined behavior，不可假設一定 wrap around。`malloc` 回傳的記憶體未初始化，讀取前要先寫入或使用 `calloc`。

## 練習前檢查

每個陣列存取是否在界內？字串是否有 null terminator？函式是否真的能改到呼叫端資料？輸入是否使用有長度限制的 API，如 `fgets`？
