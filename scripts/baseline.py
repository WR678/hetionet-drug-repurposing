"""Common-neighbour baseline: score a compound–disease pair by the number of
nodes linked to both, in the same graph the R-GCN sees (the message edges and
the training CtD pairs, as an undirected graph without edge types).

Usage: python -m scripts.baseline data/processed/graph.npz SPLIT.npz OUT.tsv
"""

import sys

import numpy as np
import pandas as pd
import scipy.sparse as sp

from scripts.linkpred import load_npz, message_edges


def score_table(split, score):
    """One row per test pair: its set (positive, random or degree) and score."""
    rows = []
    for name, key in [("positive", "test"), ("random", "test_random"), ("degree", "test_degree")]:
        pairs = split[key]
        rows.append(pd.DataFrame({"compound": pairs[:, 0], "disease": pairs[:, 1],
                                  "set": name, "score": score(pairs)}))
    return pd.concat(rows, ignore_index=True)


def main(graph_path, split_path, out):
    graph = load_npz(graph_path)
    split = load_npz(split_path)
    src, dst, _, _ = message_edges(graph, split["train"])
    n = len(graph["node_id"])
    adj = sp.csr_matrix((np.ones(len(src)), (src, dst)), shape=(n, n))
    adj.data[:] = 1.0  # several edge types between the same two nodes count once

    def score(pairs):
        return np.asarray(adj[pairs[:, 0]].multiply(adj[pairs[:, 1]]).sum(axis=1)).ravel()

    score_table(split, score).to_csv(out, sep="\t", index=False)


if __name__ == "__main__":
    main(*sys.argv[1:])
