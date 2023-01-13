import numpy  as np
import networkx as nx
import matplotlib.pyplot as plt
import random
import math

N = 10 #ノード数
K = 4 #平均次数
P = 1 #リンクを再接続する確率
th_min=-math.pi#初期位相の最小値
th_max=math.pi#初期位相の最大値
w_min=0.7#固有振動数の最小値
w_max=1#固有振動数の最大値
sigma=1#結合強度
dT = 0.02#時間刻み
T = 20#時間

imageNum = 0
#グラフを表示
def draw_graph(G,pos,show=True):
    #グラフの描画
    plt.figure(figsize=(10,10))
    #sinθによってノードを大小させる
    th = nx.get_node_attributes(G, 'th')
    nx.draw_networkx_nodes(G, pos, node_size=[(math.sin(v)+1)*200 for v in th.values()],node_color="red" )#
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.axis('off')
    if show:
        plt.show()
    #画像を保存
    global imageNum
    plt.savefig("images/image"+str(imageNum)+".png")
    imageNum += 1
    plt.close()

def runge_kutta(G,dT,sigma,i):
    #sin(θi−θj)の平均を計算
    th_sum = 0
    nei_cnt = 0
    nei = G.neighbors(i)
    for j in nei:
        nei_cnt += 1
        th_sum += math.sin(G.nodes[j]['th'] - G.nodes[i]['th'])
    k1 = dT * (G.nodes[i]['freq'] + sigma * th_sum / nei_cnt)
    #sin(θi−θj)の平均を計算
    th_sum = 0
    for j in nei:
        th_sum += math.sin(G.nodes[j]['th'] - (G.nodes[i]['th'] + k1/2))
    k2 = dT * (G.nodes[i]['freq'] + sigma * th_sum / nei_cnt)
    #sin(θi−θj)の平均を計算
    th_sum = 0
    for j in nei:
        th_sum += math.sin(G.nodes[j]['th'] - (G.nodes[i]['th'] + k2/2))
    k3 = dT * (G.nodes[i]['freq'] + sigma * th_sum / nei_cnt)
    #sin(θi−θj)の平均を計算
    th_sum = 0
    for j in nei:
        th_sum += math.sin(G.nodes[j]['th'] - (G.nodes[i]['th'] + k3))
    k4 = dT * (G.nodes[i]['freq'] + sigma * th_sum / nei_cnt)
    return (k1 + 2*k2 + 2*k3 + k4) / 6 

def euler(G,dT,sigma,i):
    th_sum = 0
    nei_cnt = 0
    nei = G.neighbors(i)
    for j in nei:
        nei_cnt += 1
        th_sum += math.sin(G.nodes[j]['th'] - G.nodes[i]['th'])
    k1 = dT * (G.nodes[i]['freq'] + sigma * th_sum / nei_cnt)
    return k1

#つぎの時刻の位相を計算
def calc_next(G,dT,sigma,N):
    for i in range(N):
        #ノードiの位相を更新(euler法)
        G.nodes[i]['th'] += euler(G,dT,sigma,i)
        #G.nodes[i]['th'] += runge_kutta(G,dT,sigma,i)
#秩序パラメータを計算
def calc_orderR(G):
    n = len(G.nodes)
    #1/N*sum(e^iθ)を計算
    th_sum = 0
    for i in G.nodes:
        th_sum += math.e**(1j*G.nodes[i]['th'])
    th_avg = th_sum / n
    #|1/N*sum(e^iθ)|を計算
    return abs(th_avg)

#一次近傍コヒーレンスを計算
def calc_orderR1(G):
    n = len(G.nodes)
    sum = 0
    for i in G.nodes:
        th_sum = 0
        th_cnt = 0
        nei = G.neighbors(i)
        for j in nei:
            th_sum += math.e**(1j*(G.nodes[i]['th']-G.nodes[j]['th']))
            th_cnt += 1
        th_avg = abs(th_sum / th_cnt)
        sum += th_avg    
    avg = sum / n
    return avg

def simulateOnce(G,T=T,dT=dT,sigma=sigma,draw=True,log=True,Rmode='R'):
    #蔵本モデルで時刻t=0からt=Tまでの位相をt刻みで計算
    interval = T/100

    R = calc_orderR(G) if Rmode=='R' else calc_orderR1(G) #秩序パラメータの時間平均
    for t in np.arange(0,T,dT):
        calc_next(G,dT,sigma,G.number_of_nodes())
        #秩序パラメータを計算
        r = calc_orderR(G) if Rmode=='R' else calc_orderR1(G)
        if log:
            print(round(t,1),r)
        R+=r
        if draw and int(t*10000)%int(interval*10000)==0:
            draw_graph(G,pos,show=False)
    R=R/(T/dT+1)#平均   
    return R
if __name__ == '__main__':
    #無向グラフを生成
    while True:
        G =  nx.watts_strogatz_graph(N, K, P) 
        if nx.is_connected(G):
            break
    #ノードの位置を決定
    pos = nx.spring_layout(G)
    #各ノードに初期位相と固有振動数を設定
    for i in range(N):
        G.nodes[i]['th'] = random.uniform(th_min, th_max)
        G.nodes[i]['freq'] = random.uniform(w_min, w_max)
    R = simulateOnce(G,T=T,dT=dT,sigma=sigma,draw=True,log=True,Rmode='R1')
    print("R=",R)