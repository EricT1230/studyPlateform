# 邏輯與證明

## 核心概念

命題邏輯處理真值與推論形式；謂詞邏輯加入量詞與變數範圍。`P => Q` 等價於 `not P or Q`，其逆否命題是 `not Q => not P`。De Morgan law 會同時改變連接詞與否定位置：`not(P and Q)=not P or not Q`。全稱命題要證所有情況，存在命題只需建構一個例子。形式化的好處是能把直覺推論拆成可檢查的步驟。

## 解題重點

直接證明適合從假設一路推到結論；逆否命題適合處理「若結論不成立」較容易的題；反證法是假設命題為假並推出矛盾。數學歸納需有 base case 與 induction step；strong induction 可使用所有較小情況。要推翻全稱命題，找一個 counterexample 通常最有效。演算法或狀態轉換題常用 invariant：初始成立，操作後仍成立，目標若違反它就不可達。

## 常見陷阱

不要把 converse 當成原命題。量詞順序會改變意思，`exists x forall y` 與 `forall y exists x` 通常不同。反證法不是假設結論成立；歸納法也不能只驗幾個例子。Resolution、modus ponens、invariant 等工具都要先確認前提形式正確。

## 練習前檢查

先寫出命題的 `P` 與 `Q`，再決定證法。量詞的 domain 是什麼？否定式是否正確推進到最內層？若用反例，是否真的滿足前提且違反結論？
