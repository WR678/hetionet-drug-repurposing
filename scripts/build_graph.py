"""Build the graph for link prediction from Hetionet v1.0.

Keeps the compounds, diseases and genes, the edge types listed under
`message_edges` in the settings, and the known compound–disease pairs.

Usage: python -m scripts.build_graph config/config.yaml data/processed/graph.npz
"""

import sys

import numpy as np

from scripts.hetionet import load_edges, load_nodes
from scripts.linkpred import load_config

KINDS = ["Compound", "Disease", "Gene"]


def main(config_path, out):
    config = load_config(config_path)
    nodes = load_nodes(config["nodes"])
    nodes = nodes[nodes["kind"].isin(KINDS)].reset_index(drop=True)
    index = dict(zip(nodes["id"], range(len(nodes))))
    edges = load_edges(config["edges"])

    relations = config["message_edges"]
    msg = edges[edges["metaedge"].isin(relations)]
    rel_number = {name: i for i, name in enumerate(relations)}

    def pairs(metaedge):
        sub = edges[edges["metaedge"] == metaedge]
        return np.column_stack([sub["source"].map(index), sub["target"].map(index)]).astype(np.int64)

    compounds = np.flatnonzero(nodes["kind"] == "Compound")
    diseases = np.flatnonzero(nodes["kind"] == "Disease")
    local = np.full(len(nodes), -1, dtype=np.int64)
    local[compounds] = np.arange(len(compounds))
    local[diseases] = np.arange(len(diseases))
    target = pairs(config["target"])
    known = np.concatenate([pairs(m) for m in config["known_pairs"]])

    np.savez_compressed(
        out,
        node_id=nodes["id"].to_numpy(dtype=str),
        node_name=nodes["name"].to_numpy(dtype=str),
        compounds=compounds,
        diseases=diseases,
        local=local,
        relations=np.array(relations),
        msg_src=msg["source"].map(index).to_numpy(np.int64),
        msg_dst=msg["target"].map(index).to_numpy(np.int64),
        msg_rel=msg["metaedge"].map(rel_number).to_numpy(np.int64),
        target=target,
        known=known,
    )
    print(f"{len(nodes)} nodes ({len(compounds)} compounds, {len(diseases)} diseases), "
          f"{len(msg)} message edges of {len(relations)} types, "
          f"{len(target)} {config['target']} pairs, {len(known)} known pairs")


if __name__ == "__main__":
    main(*sys.argv[1:])
