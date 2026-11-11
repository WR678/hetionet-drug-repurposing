"""Load the Hetionet v1.0 node and edge tables, used by the report.

Paths are relative to the project folder; `pixi run download` puts the files
there. Only pandas is needed.
"""

import pandas as pd

NODES = "data/raw/hetionet/hetionet-v1.0-nodes.tsv"
EDGES = "data/raw/hetionet/hetionet-v1.0-edges.sif.gz"


def load_nodes(path=NODES):
    """One row per node: id, name and kind (node type)."""
    return pd.read_csv(path, sep="\t")


def load_edges(path=EDGES):
    """One row per edge: source, metaedge and target, plus the kinds of both ends.

    The kind of a node is the part of its id before "::", for example "Gene"
    in "Gene::3149".
    """
    edges = pd.read_csv(path, sep="\t")
    edges["source_kind"] = edges["source"].str.split("::").str[0]
    edges["target_kind"] = edges["target"].str.split("::").str[0]
    return edges


def edge_types(edges):
    """Number of edges of each type and the node kinds it connects, largest first."""
    return (edges.groupby(["metaedge", "source_kind", "target_kind"])
                 .size().rename("edges").reset_index()
                 .sort_values("edges", ascending=False, ignore_index=True))
