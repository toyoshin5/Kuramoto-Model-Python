import numpy  as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import math
import time

N = 20 #ノード数
K = 8 #平均次数
P = 0.1 #リンクを再接続する確率
th_min=-math.pi#初期位相の最小値
th_max=math.pi#初期位相の最大値
w_min=0.7#固有振動数の最小値
w_max=1#固有振動数の最大値
sigma=1#結合強度
dT = 0.1#時間刻み
T = 300#時間
ims = []

imageNum = 0
#グラフを表示
def draw_graph(G,pos,show=True):
    #グラフの描画
    plt.figure(figsize=(10,10))
    #sinθによってノードを大小させる
    th = nx.get_node_attributes(G, 'th')
    nx.draw_networkx_nodes(G, pos, node_size=[(math.sin(v)+1)*200 for v in th.values()],node_color="red" )#
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    #nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif',labels={i:round(th[i],2) for i in th})
    plt.axis('off')
    if show:
        plt.show()
    #画像を保存
    global imageNum
    plt.savefig("images/image"+str(imageNum)+".png")
    imageNum += 1
    plt.close()

#無向グラフを生成
G = nx.watts_strogatz_graph(N, K, P) 
pos = nx.spring_layout(G)
#各ノードに初期位相と固有振動数を設定
for i in range(N):
    G.nodes[i]['th'] = random.uniform(th_min, th_max)
    G.nodes[i]['freq'] = random.uniform(w_min, w_max)
#draw_graph(G,pos)
#蔵本モデルで時刻t=0からt=Tまでの位相をt刻みで計算
for t in np.arange(0,T,dT):
    for i in range(N):
        #ノードiの周りのノードの位相の平均を計算
        th_sum = 0
        nei_cnt = 0
        for j in G.neighbors(i):
            nei_cnt += 1
            th_sum += G.nodes[j]['th']
        th_avg = th_sum / nei_cnt
        #ノードiの位相を更新(オイラー法)
        G.nodes[i]['th'] += dT * (G.nodes[i]['freq'] + sigma * math.sin(th_avg - G.nodes[i]['th']))
    #tが整数なら
    if t%1 == 0:
        draw_graph(G,pos,False)