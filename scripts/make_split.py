"""Split the known treatments (CtD pairs) into training, validation and test
sets for one random seed, and draw the negative pairs for evaluation.

Two kinds of negatives are drawn for the test set, the same number as the
test positives each:

- random: a compound and a disease drawn uniformly;
- degree-matched: a compound drawn from the compounds of the test positives
  and a disease drawn from their diseases, so that the negatives have the same
  numbers of known treatments as the positives.

Negatives never include a known pair (CtD or CpD) and never repeat.

Usage: python -m scripts.make_split config/config.yaml data/processed/graph.npz SEED OUT.npz
"""

import sys

import numpy as np

from scripts.linkpred import load_config, load_npz, pair_mask


def draw_negatives(rng, n, compounds, diseases, taken, graph):
    """Draw n pairs from the given compound and disease lists (with
    replacement) that are not yet in `taken`; mark them as taken."""
    out = []
    while len(out) < n:
        c = rng.choice(compounds)
        d = rng.choice(diseases)
        i, j = graph["local"][c], graph["local"][d]
        if not taken[i, j]:
            taken[i, j] = True
            out.append((c, d))
    return np.array(out, dtype=np.int64)


def main(config_path, graph_path, seed, out):
    config = load_config(config_path)
    graph = load_npz(graph_path)
    rng = np.random.default_rng(int(seed))

    target = graph["target"]
    order = rng.permutation(len(target))
    n_test = round(config["test_fraction"] * len(target))
    n_val = round(config["val_fraction"] * len(target))
    test = target[order[:n_test]]
    val = target[order[n_test:n_test + n_val]]
    train = target[order[n_test + n_val:]]

    taken = pair_mask(graph["known"], graph)
    ratio = config["negatives_per_positive"]
    val_random = draw_negatives(rng, ratio * len(val), graph["compounds"], graph["diseases"], taken, graph)
    test_random = draw_negatives(rng, ratio * len(test), graph["compounds"], graph["diseases"], taken, graph)
    test_degree = draw_negatives(rng, ratio * len(test), test[:, 0], test[:, 1], taken, graph)

    np.savez_compressed(out, train=train, val=val, test=test, val_random=val_random,
                        test_random=test_random, test_degree=test_degree)
    print(f"seed {seed}: {len(train)} training, {len(val)} validation and {len(test)} test pairs; "
          f"{len(val_random)} + {len(test_random)} random and {len(test_degree)} degree-matched negatives")


if __name__ == "__main__":
    main(*sys.argv[1:])
