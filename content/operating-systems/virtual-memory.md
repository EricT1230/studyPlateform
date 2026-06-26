# 虛擬記憶體

## 核心概念
虛擬記憶體讓每個 process 看到獨立的位址空間，OS 與硬體再把 virtual page 映射到 physical frame。Page table 保存映射、權限、valid、dirty 等資訊；TLB 快取最近轉換，避免每次都查記憶體中的頁表。

```
virtual address = page number + offset
page table：page → frame
```

Demand paging 只在頁被實際存取時載入。若頁不在記憶體，page fault 交由 OS 找 frame、必要時換出犧牲頁、讀入資料後重試指令。
本章的核心問題是「位址轉換成本」與「實體記憶體不足」：TLB 降低轉換成本，置換演算法降低缺頁成本，工作集模型則用來判斷目前給的 frame 是否足夠。
先分清硬體快取失敗、權限失敗與頁面不在記憶體。

## 解題重點
- TLB miss 只是轉換快取沒命中，不一定 page fault。
- Effective access time 要把 fault rate 與服務時間換成同一單位。
- FIFO、LRU、Clock、OPT 的差異在於選哪個頁換出。
- Working set 不足會造成 thrashing。

## 常見陷阱
Paging 消除外部碎片，但仍有最後一頁用不滿的內部碎片。Protection fault 與 page not present 都可能表現為 fault，但原因不同。Copy-on-write 先共享唯讀頁，寫入時才複製，不是立刻複製整個位址空間。

## 練習前檢查
你應能分清 page/frame/TLB/page fault，手算 page offset 與有效存取時間，並說明 multilevel page table、inverted page table、huge pages、Belady's anomaly 與 Clock 近似 LRU。
