# Analysis decisions

One line per decision, with the date and the reason. The settings themselves
are in `config/config.yaml`.

- 2026-11-17: split the 755 CtD pairs at random into 80% training, 10%
  validation and 10% test pairs, once per seed (0, 1, 2). This is the held-out
  link evaluation of the proposal, and the common-neighbour baseline can be
  scored on the same pairs. Holding out whole diseases was considered and left
  for later.
- 2026-11-17: evaluate against two kinds of negatives, one of each per test
  pair: random compound–disease pairs, and degree-matched pairs drawn from the
  compounds and diseases of the test pairs. The data report shows that the
  number of known treatments per disease ranges from 1 to 68, so a model can
  score well by ranking diseases that already have many treatments; the
  degree-matched negatives measure what is left once that is controlled.
  Training uses random negatives. Known treatments (CtD) and palliative uses
  (CpD) are never negatives.
- 2026-11-17: message passing uses the edge types of the proposal: compound–gene
  (CbG, CuG, CdG), disease–gene (DaG, DuG, DdG), compound–compound (CrC) and
  disease–disease (DrD), plus the training CtD pairs. Gene–gene interactions and
  the full Hetionet were considered; they would double or multiply the running
  time and change the proposal.
- 2026-11-17: model settings: two R-GCN layers, 64-dimensional learnable node
  embeddings, DistMult decoder, Adam with learning rate 0.01, at most 200 epochs
  with early stopping on validation AP (patience 20). No hyperparameter search,
  so that `pixi run reproduce` stays within a few minutes on a CPU.
- 2026-11-17: in each epoch 30% of the training CtD pairs are scored and the
  other 70% pass messages, so the model never scores a pair it also receives
  as an edge.
- 2026-11-17: PyTorch runs with two threads, set in the settings rather than by
  the number of Snakemake cores, because the thread count can change the
  results of floating-point sums. Two runs with `--cores 2` and `--cores 4` gave
  identical test scores.
