"""Evaluate the R-GCN and the baseline on the test sets of all seeds, and rank
new compound–disease pairs with the R-GCN.

Reads results/baseline/seed{S}.tsv and results/rgcn/seed{S}_test.tsv and
seed{S}_all_pairs.npy for every seed in the settings. Writes:

- metrics_by_seed.tsv: AUROC and average precision (AP) for each model, seed
  and kind of negatives;
- metrics.tsv: their mean and standard deviation over the seeds;
- candidates.tsv: the compound–disease pairs with the highest R-GCN score,
  averaged over the seeds, among the pairs that are not known (CtD or CpD).

Usage: python -m scripts.evaluate config/config.yaml data/processed/graph.npz OUT_BY_SEED OUT_METRICS OUT_CANDIDATES
"""

import sys

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from scripts.linkpred import load_config, load_npz, pair_mask

SCORES = {"R-GCN": "results/rgcn/seed{}_test.tsv", "Common neighbours": "results/baseline/seed{}.tsv"}


def main(config_path, graph_path, out_by_seed, out_metrics, out_candidates):
    config = load_config(config_path)
    graph = load_npz(graph_path)

    rows = []
    for model, pattern in SCORES.items():
        for seed in config["seeds"]:
            scores = pd.read_csv(pattern.format(seed), sep="\t")
            positives = scores[scores["set"] == "positive"]
            for negatives in ["random", "degree"]:
                test = pd.concat([positives, scores[scores["set"] == negatives]])
                labels = test["set"] == "positive"
                rows.append({"model": model, "negatives": negatives, "seed": seed,
                             "auroc": roc_auc_score(labels, test["score"]),
                             "ap": average_precision_score(labels, test["score"])})
    by_seed = pd.DataFrame(rows)
    by_seed.to_csv(out_by_seed, sep="\t", index=False)
    summary = (by_seed.groupby(["model", "negatives"], sort=False)[["auroc", "ap"]]
               .agg(["mean", "std"]))
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary.reset_index().to_csv(out_metrics, sep="\t", index=False)

    probs = np.stack([np.load(f"results/rgcn/seed{seed}_all_pairs.npy") for seed in config["seeds"]])
    mean, sd = probs.mean(axis=0), probs.std(axis=0, ddof=1)
    mean[pair_mask(graph["known"], graph)] = -np.inf
    top = np.argsort(mean, axis=None)[::-1][:config["candidates"]]
    i, j = np.unravel_index(top, mean.shape)
    names = graph["node_name"]
    pd.DataFrame({
        "rank": np.arange(1, len(top) + 1),
        "compound": names[graph["compounds"][i]],
        "disease": names[graph["diseases"][j]],
        "probability": mean[i, j],
        "sd": sd[i, j],
    }).to_csv(out_candidates, sep="\t", index=False)


if __name__ == "__main__":
    main(*sys.argv[1:])
