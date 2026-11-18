# scripts

Code you write: Python scripts, shell scripts, small helpers.

- Run scripts from the project folder (`pixi run python scripts/x.py`), and use
  paths relative to the project folder, never absolute paths like `/Users/me/...`.
- Turn repeated commands into Pixi tasks in `pixi.toml`.

The link-prediction steps are run by the Snakemake workflow
(`workflow/Snakefile`) as modules from the project folder, for example
`python -m scripts.build_graph config/config.yaml data/processed/graph.npz`:

| Script | Step |
|--------|------|
| `download_data.py` | Download Hetionet and verify its checksums |
| `hetionet.py` | Load the node and edge tables (used by the report) |
| `linkpred.py` | Shared helpers: settings, graph and split files, message edges |
| `build_graph.py` | Graph of compounds, diseases and genes, and the known pairs |
| `make_split.py` | Training, validation and test pairs and negatives for one seed |
| `baseline.py` | Common-neighbour scores of the test pairs |
| `train_rgcn.py` | Train the R-GCN for one seed and score the test pairs and all compound–disease pairs |
| `evaluate.py` | AUROC and AP over the seeds, and the top-ranked new pairs |
