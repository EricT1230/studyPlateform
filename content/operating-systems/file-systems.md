# 檔案系統

## 核心概念
檔案系統把 block device 包裝成「命名檔案、目錄、metadata 與權限」。Unix-like 系統中，inode 保存大小、權限、擁有者與資料區塊位置；檔名通常存在目錄項目，目錄項目再指向 inode。

```
path → directory entries → inode → data blocks
```

資料配置可用連續區段、鏈結、索引或 extents；free-space bitmap 用 bit 追蹤哪些 block 可用。Page cache 讓讀寫先命中記憶體，降低裝置 I/O。
這章常考抽象與崩潰後狀態：應用看到的是 path 與 file descriptor，但系統真正要維護的是目錄、inode、bitmap、資料區塊之間的一致性。
因此要分清名稱操作與資料落盤是兩個層次。

## 解題重點
- Hard link 是多個名稱指同一 inode；symlink 是一個存路徑的獨立檔案。
- Journaling 先記錄交易，崩潰後可 replay 或 rollback metadata。
- Copy-on-write 不覆寫舊 block，適合快照。
- `fsync` 用來要求資料或 metadata 更接近持久化保證。

## 常見陷阱
`write()` 成功通常只代表 kernel 收下資料，不等於斷電後一定存在。刪檔是移除目錄項並降低 link count，不一定立刻清資料。RAID 或快照都不能取代備份。Metadata 寫入順序錯誤會造成不一致。

## 練習前檢查
你應能分清 inode 與檔名、hard link 與 symlink，並說明 allocation、bitmap、journaling、fsck、log-structured FS、atomic rename 與 client-side caching 的基本取捨。
