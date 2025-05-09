#!/usr/bin/env python3
"""Discrete‑time proof‑of‑concept simulator."""

import numpy as np, argparse, json, os, sys, time
import networkx as nx
from collections import deque
from pathlib import Path
from topology import build_grid
from scheduler import HopAwareScheduler
from traffic import poisson_arrivals

class Packet:
    __slots__ = ('dst','cls','hop','birth')
    def __init__(self,dst,cls,birth):
        self.dst=dst; self.cls=cls; self.hop=0; self.birth=birth

class Node:
    def __init__(self,F):
        self.queues=[deque() for _ in range(F+1)]
    def enqueue(self,pkt,cls):
        self.queues[cls].append(pkt)
    def has_packets(self):
        return any(self.queues[f] for f in range(len(self.queues)))
    def pop_by_policy(self,weights):
        # sample on simplex until we hit non‑empty queue
        F=len(weights)-1
        while True:
            cls=np.random.choice(F+1,p=weights)
            if self.queues[cls]:
                return cls,self.queues[cls].popleft()
            # if chosen empty, fall back to scan
            for f in range(F+1):
                if self.queues[f]:
                    return f,self.queues[f].popleft()
            return None,None

def run(args):
    np.random.seed(args.seed)
    G=build_grid(args.rows,args.cols)
    N=G.number_of_nodes()
    # build hop feasibility mask for OD pairs
    od_pairs=[(u,v) for u in range(N) for v in range(N) if u!=v]
    P=len(od_pairs)
    H=np.zeros((P,args.F+1),dtype=int)
    for idx,(u,v) in enumerate(od_pairs):
        hop=len(nx.shortest_path(G,u,v))-1
        if hop>args.hopmax:
            H[idx,1:]=1  # mark infeasible for all priority classes
    scheduler=HopAwareScheduler(args.F,H,mu=args.S)
    nodes=[Node(args.F) for _ in range(N)]
    results=[]
    global_time=0
    for frame in range(args.frames):
        # arrival phase
        arrivals=poisson_arrivals(np.array(args.lam))
        for n in range(N):
            for f,count in enumerate(arrivals,1):  # classes start at 1
                for _ in range(count):
                    dst=np.random.randint(0,N-1)
                    if dst>=n: dst+=1
                    nodes[n].enqueue(Packet(dst,f,global_time),f)
        # scheduler step
        pq=scheduler.step(np.array(args.lam))
        delivered=0; dropped=0; latency=[]
        # service S slots
        for slot in range(args.S):
            for n in range(N):
                cls,pkt=nodes[n].pop_by_policy(pq)
                if pkt is None: continue
                if pkt.hop+1 > args.hopmax:
                    dropped+=1; continue
                try:
                    path=nx.shortest_path(G,n,pkt.dst)
                    if pkt.hop+1 >= len(path):
                        dropped+=1; continue
                    next_hop=path[pkt.hop+1]
                    pkt.hop+=1
                    if next_hop==pkt.dst:
                        delivered+=1
                        latency.append(global_time+slot - pkt.birth +1)
                    else:
                        nodes[next_hop].enqueue(pkt, cls)
                except (nx.NetworkXNoPath, IndexError):
                    dropped+=1; continue
        results.append({'frame':frame,'delivered':delivered,'dropped':dropped,
                        'pdr':delivered/max(delivered+dropped,1),
                        'latency':np.mean(latency) if latency else 0})
        global_time+=args.S
    # write results
    Path("results").mkdir(exist_ok=True)
    with open("results/run.jsonl","w") as f:
        for r in results: f.write(json.dumps(r)+'\n')
    summary={'mean_pdr':np.mean([r['pdr'] for r in results]),
             'mean_latency':np.mean([r['latency'] for r in results if r['latency']>0])}
    import pandas as pd
    pd.DataFrame([summary]).to_csv("results/summary.csv",index=False)
    print("Finished. Summary:",summary)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--rows',type=int,default=4)
    p.add_argument('--cols',type=int,default=4)
    p.add_argument('--F',type=int,default=3)
    p.add_argument('--hopmax',type=int,default=8)
    p.add_argument('--S',type=int,default=10)
    p.add_argument('--frames',type=int,default=500)
    p.add_argument('--lam',type=float,nargs='+',default=[4,4,2],
                   help='arrival rates per class (length F)')
    p.add_argument('--seed',type=int,default=0)
    args=p.parse_args()
    run(args)