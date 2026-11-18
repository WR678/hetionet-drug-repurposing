# Project structure

| Folder | What goes in it | Rule |
|--------|-----------------|------|
| `data/raw/` | Hetionet v1.0, downloaded by `scripts/download_data.py` | Read-only, not committed |
| `data/processed/` | The graph and the splits for each seed, built by the workflow | Rebuilt, not committed |
| `metadata/` | Data sources, checksums, data dictionary, licenses | Committed |
| `scripts/` | Download, graph, split, baseline, R-GCN and evaluation code | Committed |
| `config/` | Workflow and model settings (`config.yaml`) | Committed |
| `workflow/` | `Snakefile` | Committed |
| `notebooks/` | Exploration (`explore-hetionet.ipynb`), outputs cleared | Committed |
| `reports/` | Quarto report source and bibliography | Source committed, HTML not |
| `results/` | Everything the workflow produces | Rebuilt, not committed |
| `docs/` | This file, the decision log, the paper audit, software versions, the rule graph | Committed |
| `envs/` | Conda exports of the Pixi environment | Generated |
| `containers/` | `Dockerfile` and `apptainer.def`, built from `pixi.lock` | Committed |
| `.github/workflows/` | The reproduce-from-a-clean-clone check | Committed |

The layout comes from the CBIO7501 project template
(<https://github.com/khan-lab/cbio7501-f26/tree/main/templates/cookiecutter-repro-project>).
