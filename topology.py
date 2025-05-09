import networkx as nx
import numpy as np
import csv
from pathlib import Path

def build_grid(m: int, n: int, spacing: float = 200.0):
    """Return an m×n grid graph with unit‑weight edges."""
    G = nx.grid_2d_graph(m, n)
    mapping = {v: i for i, v in enumerate(G.nodes)}
    G = nx.relabel_nodes(G, mapping)
    return G

def load_topology_csv(path: str):
    """Read edge list CSV with two integer columns u,v."""
    G = nx.Graph()
    with open(path, newline='') as f:
        rdr = csv.reader(f)
        for u,v in rdr:
            G.add_edge(int(u), int(v))
    return G

def flow_incidence(G, F):
    """Return list of OD pairs and flow–class incidence H (P×(F+1))."""
    nodes = list(G.nodes)
    od_pairs = [(u,v) for u in nodes for v in nodes if u!=v]
    P = len(od_pairs)
    H = np.zeros((P, F+1), dtype=int)
    return od_pairs, H
