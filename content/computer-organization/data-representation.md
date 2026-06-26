# 資料表示法

## 核心概念
資料表示法的關鍵是「同一串 bit 由誰解讀」。unsigned 把每個位元當正權重；two's complement 用最高位代表負權重，n-bit 範圍是 `-2^(n-1)` 到 `2^(n-1)-1`。十六進位每一位等於 4 bits，常用來緊湊表示 byte。

```
0x3A = 0011 1010
little-endian：低位 byte 放低位址
big-endian：高位 byte 放低位址
```

浮點數用 sign、biased exponent、fraction 近似實數；字元則要分清 Unicode code point 與 UTF-8 byte 編碼。
固定寬度是這章的核心限制：同樣的加法、位移或型別轉換，只要位元數不同，結果、溢位與補位方式都可能改變。做題時不要只算數值，也要追蹤 bit pattern。
若遇到轉型題，先寫出原始位元，再決定是零擴展、符號擴展或重新解讀。

## 解題重點
- 先確認題目要 signed、unsigned、固定寬度或最少位元數。
- sign extension 要複製符號位，不是補 0。
- signed overflow 看「同號相加卻變異號」。
- bit mask：OR 設 1、AND 清除或保留、XOR 翻轉。

## 常見陷阱
Carry 與 signed overflow 不是同一件事。`0.1` 這類十進位小數常無法被二進位浮點精確表示。Struct padding 來自 alignment，不是資料被改寫。Endianness 影響記憶體 byte 順序，不改變數值本身。

## 練習前檢查
你應能換算二進位與十六進位、推導 two's complement 範圍、辨識 endian byte 排列，並說明浮點誤差、NaN、subnormal 與 UTF-8 相容 ASCII 的原因。
