# 估計與假設檢定

## 核心概念

Estimator 是抽樣前的規則或隨機變數，estimate 是代入資料後的數值。Unbiased 表示 `E[theta_hat]=theta`，不代表每次都準。Standard error 是估計量抽樣分布的標準差。Confidence interval 在 frequentist 語境中描述長期覆蓋率；95% 指重複抽樣產生的區間程序約 95% 會覆蓋真參數。Consistency 則看樣本數變大時估計量是否收斂到真值。

## 解題重點

MLE 會選擇讓觀察資料 likelihood 最大的參數。Hypothesis testing 要先分清 `H0`、`H1`、顯著水準與檢定統計量。p-value 是在 `H0` 為真時，得到至少如此極端結果的機率。Type I error 是真 `H0` 被拒絕；power 是 alternative 為真時拒絕 `H0` 的機率。MSE 可拆成 `Var(theta_hat)+Bias(theta_hat)^2`，用來比較偏差與變異的取捨。

## 常見陷阱

p-value 不是 `H0` 為真的機率。樣本變異數用 `n-1` 是為了修正用 sample mean 帶來的自由度損失。樣本數增加通常讓 interval 變窄，但不能消除模型假設錯誤。多重檢定會提高整體 false positive 風險，需要 correction。

## 練習前檢查

已知母體變異數嗎？若未知且近似 normal，是否該用 t distribution？檢定是單尾還是雙尾？CI 與雙尾 test 的對偶關係是否能用來交叉檢查結論？樣本假設、獨立性與近似條件是否寫清楚？
