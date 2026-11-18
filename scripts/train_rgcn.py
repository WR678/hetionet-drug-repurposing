"""Train the relational graph convolutional network (R-GCN) for one seed.

The model has a learnable embedding for every node, R-GCN layers with one
weight matrix per relation and direction (Schlichtkrull et al. 2018), and a
DistMult decoder that scores a compound–disease pair. It is trained with
binary cross-entropy against random negative pairs. In each epoch a random
share (`supervision_fraction`) of the training CtD pairs is scored and the
other training pairs pass messages, so the model never scores a pair that it
also sees as an edge. Training stops when the average precision on the
validation set has not improved for `patience` epochs, and the model from the
best epoch is kept.

Usage:
  python -m scripts.train_rgcn config/config.yaml data/processed/graph.npz SPLIT.npz SEED \
      TEST_SCORES.tsv TRAINING_LOG.tsv ALL_PAIRS.npy
"""

import copy
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import average_precision_score
from torch_geometric.nn import RGCNConv

from scripts.baseline import score_table
from scripts.linkpred import load_config, load_npz, message_edges, pair_mask


class RGCN(torch.nn.Module):
    def __init__(self, n_nodes, n_relations, dim, layers, dropout):
        super().__init__()
        self.embedding = torch.nn.Embedding(n_nodes, dim)
        torch.nn.init.xavier_uniform_(self.embedding.weight)
        self.convs = torch.nn.ModuleList(RGCNConv(dim, dim, n_relations) for _ in range(layers))
        self.relation = torch.nn.Parameter(torch.ones(dim))
        self.dropout = dropout

    def encode(self, edge_index, edge_type):
        x = self.embedding.weight
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index, edge_type)
            if i < len(self.convs) - 1:
                x = F.dropout(F.relu(x), self.dropout, self.training)
        return x

    def score(self, x, pairs):
        """DistMult score (a logit) of each compound–disease pair."""
        pairs = torch.as_tensor(pairs)
        return (x[pairs[:, 0]] * self.relation * x[pairs[:, 1]]).sum(-1)


def main(config_path, graph_path, split_path, seed, out_scores, out_log, out_pairs):
    config = load_config(config_path)
    settings = config["model"]
    seed = int(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(config["threads"])
    rng = np.random.default_rng(seed)

    graph = load_npz(graph_path)
    split = load_npz(split_path)
    train = split["train"]
    compounds, diseases = graph["compounds"], graph["diseases"]

    def edges(ctd_pairs):
        src, dst, rel, n_relations = message_edges(graph, ctd_pairs)
        return torch.as_tensor(np.stack([src, dst])), torch.as_tensor(rel), n_relations

    full_index, full_type, n_relations = edges(train)

    # Training negatives: any compound–disease pair that is not a known pair
    # and not a validation or test negative.
    forbidden = pair_mask(graph["known"], graph)
    for key in ["val_random", "test_random", "test_degree"]:
        forbidden |= pair_mask(split[key], graph)
    allowed = np.flatnonzero(~forbidden.ravel())

    def random_negatives(k):
        flat = rng.choice(allowed, k)
        return np.column_stack([compounds[flat // len(diseases)], diseases[flat % len(diseases)]])

    val_pairs = np.concatenate([split["val"], split["val_random"]])
    val_labels = np.r_[np.ones(len(split["val"])), np.zeros(len(split["val_random"]))]

    model = RGCN(len(graph["node_id"]), n_relations, settings["dim"], settings["layers"], settings["dropout"])
    optimizer = torch.optim.Adam(model.parameters(), lr=settings["lr"], weight_decay=settings["weight_decay"])

    log, best_ap, best_epoch, best_state = [], -1.0, 0, None
    for epoch in range(1, settings["max_epochs"] + 1):
        model.train()
        order = rng.permutation(len(train))
        n_sup = round(settings["supervision_fraction"] * len(train))
        scored, passing = train[order[:n_sup]], train[order[n_sup:]]
        edge_index, edge_type, _ = edges(passing)
        x = model.encode(edge_index, edge_type)
        logits = torch.cat([model.score(x, scored), model.score(x, random_negatives(n_sup))])
        labels = torch.cat([torch.ones(n_sup), torch.zeros(n_sup)])
        loss = F.binary_cross_entropy_with_logits(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            x = model.encode(full_index, full_type)
            val_ap = average_precision_score(val_labels, model.score(x, val_pairs).numpy())
        log.append({"epoch": epoch, "loss": loss.item(), "val_ap": val_ap})
        if val_ap > best_ap:
            best_ap, best_epoch, best_state = val_ap, epoch, copy.deepcopy(model.state_dict())
        elif epoch - best_epoch >= settings["patience"]:
            break

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        x = model.encode(full_index, full_type)
        score_table(split, lambda pairs: model.score(x, pairs).numpy()).to_csv(out_scores, sep="\t", index=False)
        all_pairs = torch.sigmoid((x[compounds] * model.relation) @ x[diseases].T)
    np.save(out_pairs, all_pairs.numpy().astype(np.float32))
    log = pd.DataFrame(log)
    log["best"] = log["epoch"] == best_epoch
    log.to_csv(out_log, sep="\t", index=False)
    print(f"seed {seed}: {len(log)} epochs, best epoch {best_epoch}, validation AP {best_ap:.3f}")


if __name__ == "__main__":
    main(*sys.argv[1:])
