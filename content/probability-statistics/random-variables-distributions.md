# 隨機變數與分布

## 核心概念

Random variable 把隨機結果映成數值。離散型用 PMF，期望為 `sum_x x P(X=x)`；連續型用 PDF，需 `f(x)>=0` 且總積分為 1。CDF 定義為 `F_X(x)=P(X<=x)`，非遞減且右連續。Variance 是 `E[(X-E[X])^2]`，衡量平均周圍的平方偏差。分布比單一摘要統計更完整；平均與變異相同的變數仍可能有完全不同的尾端行為。

## 解題重點

常見分布要連到情境：Bernoulli 是一次成功/失敗，Binomial 是固定次數成功數，Poisson 常描述稀疏計數，Geometric 與 Exponential 有 memoryless property，Normal 可經 `Z=(X-mu)/sigma` 標準化。Joint distribution 若可分解為 marginals 乘積，才是 independent。全機率與全期望可把複雜問題依條件分層，最後再加權平均。

## 常見陷阱

Mean 或 variance 相同不代表分布相同，也不代表 independent。Zero covariance 只表示無線性關係；independence 才能保證 covariance 為 0，反向一般不成立。MGF 在 0 附近存在時可取 moments，但 characteristic function 對所有 random variables 都存在。連續變數轉換時若忘記 Jacobian，密度通常會錯。

## 練習前檢查

先判斷是離散還是連續。要求機率、期望、variance、CDF 還是分布轉換？若做變數變換，是否補上 Jacobian？極限定理題是否滿足 iid 與有限 variance 等條件？收斂題要分清 almost surely、in probability 與 distribution。若用近似分布，也要註明樣本數與假設來源。
