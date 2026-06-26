# 機率基礎

## 核心概念

事件機率從樣本空間與集合運算開始。兩事件聯集公式是 `P(A union B)=P(A)+P(B)-P(A cap B)`。條件機率定義為 `P(A|B)=P(A cap B)/P(B)`，其中 `P(B)>0`。Independence 表示 `P(A cap B)=P(A)P(B)`，也可推出在 `P(B)>0` 時 `P(A|B)=P(A)`。若事件可由互斥且覆蓋樣本空間的分割描述，就能用全機率公式先拆再合。

## 解題重點

Bayes theorem 可把條件方向反轉：`P(A|B)=P(B|A)P(A)/P(B)`。期望值是加權平均，並有線性性：`E[aX+b]=aE[X]+b`。Variance 對平移不變、對縮放平方放大：`Var(aX+b)=a^2 Var(X)`。常見分布要記住 Bernoulli 的 `Var=p(1-p)`、Binomial 的機率質量與 Geometric 的 `E[X]=1/p`。中心極限定理處理的是樣本平均的近似分布，不是單一觀測值會變常態。

## 常見陷阱

互斥不等於獨立；若兩個非零機率事件互斥，反而不可能獨立。`P(A|B)` 與 `P(B|A)` 通常不同，低 base rate 會大幅影響後驗機率。PDF 可以大於 1；連續變數的單點機率為 0。Covariance 為 0 只代表沒有線性關聯，通常不能直接推 independence。

## 練習前檢查

事件是否重疊？條件機率的分母是哪個事件？是否可用 partition 套 total probability？題目問的是單一觀測值、樣本平均，還是極限定理下的近似？若宣稱獨立，能否代回定義驗算交集機率？
