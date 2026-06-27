# SQL 基礎

## 這是什麼？

SQL 是「**描述式**」語言：你只說「要什麼資料」，不用說「怎麼拿」——資料庫自己決定最有效率的取法。

生活類比：你跟店員說「給我所有紅色、500 元以下的鞋」，不用教他怎麼一櫃一櫃找。

下面用兩張小表當例子：

```
students                 enrollments
┌────┬───────┐          ┌────┬────────┐
│ id │ name  │          │ sid│ course │
├────┼───────┤          ├────┼────────┤
│ 1  │ Amy   │          │ 1  │ DB     │
│ 2  │ Ben   │          │ 1  │ OS     │
│ 3  │ Cara  │          │ 2  │ DB     │
└────┴───────┘          └────┴────────┘
                         （Cara 沒有選課紀錄）
```

## JOIN：把表接起來

**INNER JOIN**：只留「兩邊都對得上」的列。

```
SELECT name, course
FROM students JOIN enrollments ON students.id = enrollments.sid;

結果：
  Amy  | DB
  Amy  | OS
  Ben  | DB
  （Cara 沒選課 → 被排除）
```

**LEFT JOIN**：左表全留，右邊沒對到的補 NULL。

```
結果：
  Amy  | DB
  Amy  | OS
  Ben  | DB
  Cara | NULL      ← Cara 留下來了，課程是 NULL
```

→ 想找「沒選任何課的學生」就用 LEFT JOIN 再篩 `course IS NULL`。

## 子句的「邏輯執行順序」（解釋很多怪現象）

你寫的順序是 SELECT 開頭，但資料庫**實際處理**順序是：

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
 取表   篩列    分組      篩組     選欄位   排序
```

這就解釋了：為什麼 SELECT 裡取的別名常不能用在 WHERE（WHERE 比 SELECT 早跑）。

## WHERE vs HAVING

- **WHERE**：在分組「前」篩**個別列**，不能用聚合函數。
- **HAVING**：在分組「後」篩**每一組**，可以用聚合。

```
找「選超過 1 門課的學生」：
SELECT sid FROM enrollments
GROUP BY sid
HAVING COUNT(*) > 1;        ← 聚合條件要用 HAVING
```

## NULL：最容易出錯的地方

NULL 代表「未知」，**不是 0、也不是空字串**。任何和 NULL 比較都得到「未知」（非真）：

```
WHERE col = NULL     ✗ 永遠不成立！
WHERE col IS NULL    ✓ 正確寫法
```

陷阱：`NOT IN (1, 2, NULL)` 可能回**空結果**（因為和 NULL 比較變未知，整串 AND 無法為真）。清單裡有 NULL 時要特別小心。

## 幾個常考小差異

- `COUNT(*)` 數所有列；`COUNT(col)` **忽略該欄為 NULL** 的列。
- `UNION` 會**去重**；`UNION ALL` 保留重複、較快。
- `DISTINCT` 只影響**輸出**，不會清理原始資料。
- **視窗函數**（如 `RANK() OVER(...)`）能在「不縮減列數」下做排名/累計，跟 GROUP BY 把多列壓成一列不同。

## 安全：SQL injection

把使用者輸入直接字串拼進 SQL 很危險：

```
"... WHERE name = '" + input + "'"      ✗ 可被注入
```

正解：**參數化查詢 (prepared statement)**，讓輸入只被當「資料」而非 SQL 程式碼。

## 解題時的判斷

- 先標出：資料來源 (FROM)、連結條件 (ON)、分組 (GROUP BY)、篩選 (WHERE/HAVING)。
- 問「結果幾列」→ 特別注意 NULL、重複列、outer join 補的空值。
- 問「語法位置/別名能不能用」→ 回到邏輯執行順序。
- 出現子查詢 → 看它有沒有引用外層欄位（相關子查詢會逐列重算）。
