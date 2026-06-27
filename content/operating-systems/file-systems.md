# 檔案系統 (File System)

## 這是什麼？

硬碟本身只是「一大堆編號的區塊 (block)」，很難用。
檔案系統就是把它包裝成我們熟悉的「檔案、資料夾、檔名、權限」。

生活類比：硬碟像一間堆滿無標籤箱子的倉庫；檔案系統就是那本「目錄手冊」，告訴你某份文件叫什麼名字、放在哪幾個箱子。

## 從檔名到資料：三層對應

在 Unix-like 系統，「檔名」和「檔案內容」是分開的，中間靠 **inode** 串起來：

```
路徑 /home/eric/a.txt
        │
   目錄項 (directory entry)   "a.txt" → inode 42
        │
     inode 42  ┌─ 大小、權限、擁有者、時間
               └─ 指向資料區塊：[block 5][block 9][block 12]
        │
     實際資料 (data blocks)
```

- **目錄 (directory)**：其實也是一種檔案，內容是「檔名 → inode 號碼」的對照表。
- **inode**：存一個檔案的所有 metadata（大小、權限…）和「資料在哪些 block」。**注意：inode 裡沒有檔名。**

```
/                      （根目錄）
├── home
│    └── eric
│         ├── a.txt → inode 42
│         └── b.txt → inode 43
└── etc
```

## Hard link vs Symlink（高頻考點）

**Hard link（硬連結）**：另一個檔名，指向**同一個 inode**。兩個名字平等，刪掉一個，資料還在（因為還有人指著它）。

```
a.txt ─┐
       ├─▶ inode 42 ─▶ 資料        （兩個名字、同一份資料）
b.txt ─┘
```

**Symlink（符號連結 / 捷徑）**：一個**獨立的小檔案**，內容只是「另一個路徑字串」。原檔刪了，捷徑就變死連結。

```
link.txt ─▶（內容是字串 "/home/eric/a.txt"）─▶ a.txt ─▶ inode 42
```

inode 裡有個 **link count**（有幾個硬連結指著我）。刪檔其實是「移除目錄項 + link count 減 1」；要等 count 歸 0、且沒人開著它，資料才真的被回收。

## 空間配置與 free space

- 資料怎麼配：連續、鏈結、索引、或 extents（一段連續區間）。
- 哪些 block 還空著：用 **free-space bitmap**（一個 bit 代表一個 block 是否被用）。

## 崩潰一致性：journaling

問題：更新檔案要改好幾個地方（目錄項、inode、bitmap、資料）。如果改到一半斷電，檔案系統就壞了。

**Journaling（日誌）**：先把「我要做哪些變更」寫進日誌，再實際執行。斷電後重開機，照日誌 replay（補完）或 rollback（撤銷），保持一致。

## 常見誤解

- `write()` 回傳成功，**只代表 kernel 收下了**，不保證已寫到硬碟（可能還在 page cache）。要確保落盤用 `fsync`。
- 刪檔**不一定立刻清掉資料**——只是移除名字、減 link count。
- **inode 不存檔名**（檔名在目錄項裡）。
- RAID／快照**不能取代備份**（誤刪、毀損會一起同步）。

## 解題時的判斷

- 分清楚是「名稱層」操作（rename、link、unlink）還是「資料層」操作（讀寫 block）。
- hard link / symlink 題 → 先問「指的是同一個 inode，還是存路徑字串」。
- 崩潰一致性題 → 想 journaling、metadata 寫入順序、fsync。
