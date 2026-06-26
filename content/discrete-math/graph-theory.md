# 圖論

## 核心概念

Graph 由頂點與邊組成；simple graph 不含 self-loop 與 parallel edges。無向圖的 handshaking lemma 是 `sum deg(v)=2|E|`。Tree 是 connected 且 acyclic，因此 `n` 個頂點有 `n-1` 條邊。Connected 表示任兩頂點間有 path；bipartite 等價於沒有 odd cycle；planar connected graph 滿足 `V-E+F=2`。同一張圖也可用 adjacency list、matrix 或圖形描述，解題時要能在表示法之間轉換。

## 解題重點

先辨認圖是 directed、undirected、weighted、simple、connected 或 bipartite。Euler 題看 degree：Euler circuit 需要所有頂點偶度，Euler trail 則允許恰兩個奇度頂點。Hamiltonian 問的是頂點，Euler 問的是邊。最短路要確認邊權非負才可用 Dijkstra；MST 常靠 cut property 判斷安全邊。進階題若提到 matching、flow 或 Laplacian，先找它對應的結構量：鄰居集合、cut capacity 或 connected components。證明題常可從反例、度數總和或移除頂點後的連通性下手。

## 常見陷阱

Tree 沒有 cycle，但 bipartite graph 可以有偶數 cycle。Planar 不等於可用兩色，也不代表邊數任意多。Odd cycle 需要三色，不是所有 cycle 都需要三色。Directed graph 有 topological ordering 的條件是 DAG；只看無向連通性不夠。Graph coloring 問的是相鄰頂點不同色，不能只數頂點或邊。

## 練習前檢查

題目問路徑、迴路、著色、平面性、匹配還是流量？條件是否包含 connected？degree 是入度、出度還是無向 degree？演算法的前提，如非負權重或 DAG，是否已確認？
