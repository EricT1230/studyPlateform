# 路由與子網路

## 核心概念
IP 前綴用 `位址/長度` 表示網路範圍；前綴越長越具體。Router 轉送時採 longest prefix match，在所有匹配路由中選最長者。子網切割時，host bits 決定範圍大小。

```
/24：256 個位址
/26：64 個位址，傳統可用 host 約 62
```

同一 LAN 內送 frame 要知道目的 MAC，IPv4 常靠 ARP；跨網段時先送給 default gateway。NAT 會用位址與 port 映射讓多台內部主機共用 public IP。
子網題可先把前綴換成 host bits，再找倍數邊界；路由題則先列出所有匹配項，再選最長前綴。這兩步分開做，錯誤率會低很多。
若目的地不在本地子網，主機送出的乙太網路 frame 目的 MAC 會是 gateway，不是最終主機。
這是區分二層與三層轉送的關鍵。

## 解題重點
- 子網大小是 `2^(host bits)`；傳統 IPv4 扣 network 與 broadcast。
- Network address 是範圍第一個；broadcast 是最後一個。
- Private ranges：10/8、172.16/12、192.168/16。
- Distance-vector 傳距離估計；link-state 建拓撲圖；BGP 看 AS path 與政策。

## 常見陷阱
不要用十進位直覺切子網，先看 block size 是否對齊。Default route 通常是 `0.0.0.0/0`，因為任何目的都匹配但最不具體。Traceroute 是利用 TTL/hop limit 逐步過期推測路徑。

## 練習前檢查
你應能算 network/broadcast/可用 host、做 CIDR 彙總、套 longest prefix match，並說明 ARP、NAT、OSPF、RIP、BGP、ECMP 與 route filtering 的基本用途。
