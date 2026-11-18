# Hetionet drug repurposing

Prediction of drug–disease treatment relationships in the Hetionet biomedical knowledge graph using a relational graph convolutional network (R-GCN), evaluated on held-out links against a common-neighbour baseline.

Question: can an R-GCN rank held-out compound–treats–disease links in
Hetionet v1.0 better than a common-neighbour baseline, and does the answer
hold when the negative pairs are matched for the number of known treatments
of their compounds and diseases? The graph has the compounds, diseases and
genes of Hetionet with eight edge types (compound–gene, disease–gene,
compound–compound and disease–disease). The 755 known treatments are split
into training, validation and test links for three random seeds, and both
models are evaluated by AUROC and average precision against random and
degree-matched negatives. The settings and the reasons for them are in
`config/config.yaml` and `docs/decisions.md`. This is a reproducible version
of the graph-based drug repurposing question in my own research.

Author: Rui Wang (ORCID [0009-0008-5273-0060](https://orcid.org/0009-0008-5273-0060))

## Publication

None yet. The data is from Himmelstein et al. (2017), *eLife* 6:e26726,
<https://doi.org/10.7554/eLife.26726>. The model follows Schlichtkrull et al.
(2018), *The Semantic Web (ESWC 2018)*, 593–607,
<https://doi.org/10.1007/978-3-319-93417-4_38>.

## Reproduce the results

Requirements: [Pixi](https://pixi.prefix.dev/latest/) and an internet
connection. No GPU is needed.

```bash
git clone https://github.com/WR678/hetionet-drug-repurposing.git
cd hetionet-drug-repurposing
pixi run reproduce
```

`pixi run reproduce` installs the exact software versions in `pixi.lock`,
downloads the data and checks its checksums, runs the Snakemake workflow
(`workflow/Snakefile`, settings in `config/config.yaml`) and renders the
report. The workflow runs the exploration notebook, builds the graph, splits
the known treatments for three random seeds, trains the R-GCN and scores the
common-neighbour baseline for each seed, and evaluates both models. A rerun
repeats only the steps whose inputs changed. PyTorch always runs with two
threads, and two runs give identical results. A GitHub Action runs the same
command on every push. `pixi task list` shows all tasks.

`pixi.lock` pins the environment for Linux (`linux-64`), macOS on Apple
silicon and Intel (`osx-arm64`, `osx-64`) and Windows (`win-64`), with the CPU
builds of PyTorch. The project has been run only on `linux-64`: Ubuntu 26.04
under WSL2 and the GitHub Actions `ubuntu-latest` runner.

Without Pixi, Conda or Mamba users can build the environment from
`envs/environment.yml`, which carries the version ranges of `pixi.toml`, or
from the file for their platform in `envs/explicit/`, which lists the exact
packages of `pixi.lock` (for example
`conda create -p ./env --file envs/explicit/default_linux-64_conda_spec.txt`).
Both are exported with `pixi workspace export`; the Linux file was tested with
micromamba. The steps of the analysis, including `reproduce`, are Pixi tasks in
`pixi.toml`, so Conda users run their commands by hand.

## Container

The environment can also be used as a Docker image built from `pixi.lock` (Linux, amd64): `docker build --platform linux/amd64 -f containers/Dockerfile --build-arg ENV_NAME=default -t hetionet-drug-repurposing:0.1.0 .` The steps of `reproduce` ran in it with the project mounted at `/work`, on 2026-11-11, image ID `sha256:1ac5a544dc5f5d5c6fc458c966d5abb204fe7da8ce60ac1e3d19bd113b3db89e`.

## Hardware

Any laptop from the last few years. Measured on 2026-11-18 (Intel Core
i7-12700H, Ubuntu 26.04 under WSL2, 2 cores): 3.6 GB of disk for the software
environment, 15 MB for the raw data and 3 MB for the results; the whole
workflow takes about 80 seconds and at most 1.2 GB of memory.

## Outputs

| Path | Content |
|------|---------|
| `reports/hetionet-report.html` | The report: data, methods, results, the validation curves, the top-ranked new compound–disease pairs, software versions |
| `results/notebooks/explore-hetionet.html` | The executed exploration notebook |
| `results/tables/metrics.tsv` | Test AUROC and average precision, mean and SD over the seeds |
| `results/tables/metrics_by_seed.tsv` | The same for each seed |
| `results/tables/candidates.tsv` | The 20 new compound–disease pairs with the highest R-GCN score |
| `results/rgcn/`, `results/baseline/` | Test scores and training logs for each seed |

Expected test AUROC (mean over the seeds 0, 1 and 2): R-GCN 0.908 and common
neighbours 0.886 with random negatives; R-GCN 0.599 and common neighbours
0.706 with degree-matched negatives.

## Data

Hetionet v1.0 (Himmelstein et al. 2017): the node table
`hetionet-v1.0-nodes.tsv` (2.5 MB) and the edge list
`hetionet-v1.0-edges.sif.gz` (12.4 MB), from
<https://github.com/hetio/hetionet> at tag `v1.0.0` (commit `4933ca1`).
`pixi run download` (the script `scripts/download_data.py`) downloads both files into
`data/raw/hetionet/`, checks them against the provider's Git blob IDs and
our SHA-256 checksums, and makes them read-only. Sources, checksums, the data
dictionary and the licenses of the integrated resources are in `metadata/`.

## Data availability

Hetionet v1.0 is publicly available on GitHub at
<https://github.com/hetio/hetionet> (tag `v1.0.0`) and archived on Zenodo at
<https://doi.org/10.5281/zenodo.268568>. Original Hetionet content is released
under CC0; the resources it integrates keep their own licenses, listed in
`metadata/README.md`. `scripts/download_data.py` downloads every raw file from
the sources listed in `metadata/sources.tsv` and checks it against
`metadata/checksums.sha256`. Derived data and results are not distributed:
they are regenerated from the raw data by the code in this repository. Code
and environment: <https://github.com/WR678/hetionet-drug-repurposing> (MIT).

## Repository contents

See the table in `docs/structure.md` (each folder also has its own README).
Software versions are listed in `docs/software-versions.txt`, and the workflow
steps are drawn in `docs/rulegraph.svg`.

## Cite

See `CITATION.cff` (GitHub: "Cite this repository").

## License

Code: MIT (`LICENSE`). Report text and figures: CC BY 4.0. The data is
Hetionet v1.0: original Hetionet content is CC0, and the resources it
integrates keep their own licenses (see `metadata/README.md`).

## Contact

Questions and problems: open an issue on GitHub. Contributions: see
`CONTRIBUTING.md`. Everyone taking part follows `CODE_OF_CONDUCT.md`.
