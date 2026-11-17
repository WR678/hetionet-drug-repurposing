"""Shared helpers for the link-prediction steps: settings, graph and split files.

Every step is run from the project folder as a module, for example
`python -m scripts.build_graph config/config.yaml data/processed/graph.npz`.
"""

import numpy as np
import yaml


def load_config(path):
    """Read the workflow settings (config/config.yaml)."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_npz(path):
    """Read a graph or split file written by build_graph or make_split."""
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def pair_mask(pairs, graph):
    """Boolean compound × disease matrix that is True for the given pairs.

    `pairs` has one row per pair: the node index of the compound and of the
    disease.
    """
    mask = np.zeros((len(graph["compounds"]), len(graph["diseases"])), dtype=bool)
    if len(pairs):
        mask[graph["local"][pairs[:, 0]], graph["local"][pairs[:, 1]]] = True
    return mask


def message_edges(graph, ctd_pairs):
    """Edges for message passing: the Hetionet edges of the chosen types and the
    given CtD pairs, each also in the reverse direction as its own relation.

    Returns source nodes, target nodes and relation numbers, and the number of
    relations.
    """
    n_types = len(graph["relations"])
    src = np.concatenate([graph["msg_src"], ctd_pairs[:, 0]])
    dst = np.concatenate([graph["msg_dst"], ctd_pairs[:, 1]])
    rel = np.concatenate([graph["msg_rel"], np.full(len(ctd_pairs), n_types)])
    n_rel = n_types + 1
    return (np.concatenate([src, dst]), np.concatenate([dst, src]),
            np.concatenate([rel, rel + n_rel]), 2 * n_rel)
