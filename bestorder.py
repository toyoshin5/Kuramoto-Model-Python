import simulate as s
import numpy  as np
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
#
#グラフのつなぎ方を変更しながらシミュレーションを繰り返し、コヒーレンス(位相の一致具合)が最大になるグラフを探す。
#todo 位相の相関を求める,R1野最適化を実装する、
#

N = 100 #ノード数
K = 4 #平均次数
P = 1 #リンクを再接続する確率
th_min=-math.pi#初期位相の最小値
th_max=math.pi#初期位相の最大値
w_min=-1#固有振動数の最小値
w_max=1#固有振動数の最大値
sigma=1#結合強度
dT = 0.1#時間刻み
T = 100#時間
def draw_graph_w(G,show=True):
    pos = nx.spring_layout(G)
    #グラフの描画
    plt.figure(figsize=(10,10))
    #freqの値によって色を変える
    freq = nx.get_node_attributes(G, 'freq')
    nx.draw_networkx_nodes(G, pos, node_size=100,node_color=list(freq.values()),cmap=plt.cm.bwr, vmin=w_min, vmax=w_max,linewidths=0.5,edgecolors='k',node_shape='^')
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.axis('off')
    #画像を保存
    plt.savefig("graph_w.png")
    if show:
        plt.show()
    plt.close()

def update_link(G):
    origG = G.copy()
    while True:
        #ランダムに1つリンクを切り離す
        i = random.randint(0,N-1)
        j = random.choice(list(G.neighbors(i)))
        G.remove_edge(i,j)
        #ランダムに1つリンクをつなぐ
        while True:
            j = random.randint(0,N-1)
            if i != j and not G.has_edge(i,j):
                G.add_edge(i,j)
                break
        if nx.is_connected(G):
            return G
        else:
            G = origG.copy()

if __name__ == '__main__':
    #無向グラフを生成
    while True:
        G =  nx.watts_strogatz_graph(N, K, P) 
        if nx.is_connected(G):
            break
    #ノードの位置を決定
    #各ノードに初期位相と固有振動数を設定
    for i in range(N):
        G.nodes[i]['th'] = random.uniform(th_min, th_max)
        G.nodes[i]['freq'] = random.uniform(w_min, w_max)
    stopCnt = 0
    step = 1
    bestR = 0
    bestG = G.copy()
    draw_graph_w(bestG)
    while stopCnt < 500:
        #bestGのノードを一つつなぎ替える
        g = update_link(bestG.copy())
        R = s.simulateOnce(g.copy(),T=T,dT=dT,sigma=sigma,draw=False,log=False,R=False)
        if R > bestR:
            #ネットワーク特徴量C,L,Wを計算
            C = nx.average_clustering(g)
            L = nx.average_shortest_path_length(g)
            w = list(nx.get_node_attributes(g, 'freq').values())
            meanw = np.mean(w)
            #隣接行列
            a = nx.to_numpy_array(g)
            bunsi = 0
            bunbo = 0
            for i in range(N):
                for j in range(N):
                    bunsi+=a[i][j]*(w[i]-meanw)*(w[j]-meanw)
                    bunbo+=a[i][j]*(w[i]-meanw)*(w[i]-meanw)
            W = bunsi/bunbo
            print("delta=",stopCnt ,"bestR=",bestR,"C=",C,"L=",L,"W=",W,"step=",step)
            bestR = R
            bestG = g
            step += 1
            stopCnt = 0
        stopCnt += 1
    draw_graph_w(bestG)