# metadata

Files that describe the raw data. They are small, written by hand and committed.

## sources.tsv

Where each raw file comes from. Columns: `name`; `url` (download link, fixed
to commit `4933ca1` of <https://github.com/hetio/hetionet>, the commit that
tag `v1.0.0` points to); `git_blob_sha1` (the ID that the provider's Git
repository records for the file, as listed by `git ls-tree`, copied
2026-11-02; Hetionet publishes no md5 checksums); `dest` (where the file goes
in the project).

## checksums.sha256

SHA-256 checksum of every raw file we keep. Check with
`sha256sum -c metadata/checksums.sha256`.

## Data dictionary

`hetionet-v1.0-nodes.tsv` is a tab-separated table with one row per node
(47,031 nodes):

| Column | Meaning |
|--------|---------|
| id | node type and source identifier, joined by `::` (for example `Gene::3149`) |
| name | node name (for example `HMGB3`) |
| kind | node type (11 types, for example `Compound`, `Disease`, `Gene`) |

`hetionet-v1.0-edges.sif.gz` is a gzipped tab-separated table with one row per
edge (2,250,197 edges):

| Column | Meaning |
|--------|---------|
| source | `id` of the source node |
| metaedge | abbreviation of the edge type (24 types; for example `CtD`, Compound–treats–Disease, 755 edges) |
| target | `id` of the target node |

The edge-type abbreviations are explained in
[`describe/edges/metaedges.tsv`](https://github.com/hetio/hetionet/blob/4933ca17639cdcf146f91cc44e28128cbfc6fd24/describe/edges/metaedges.tsv)
of the Hetionet repository.

## Licenses

Original Hetionet content is released under CC0. The resources that Hetionet
integrates keep their own licenses, listed in the
[source license table](https://github.com/dhimmel/integrate/blob/d482033bcaa913a976faf4a6ee08497281c739c3/licenses/README.md)
of the Hetionet build repository. The TSV files used here do not record the
license of each node and edge; the JSON and Neo4j releases of Hetionet do.
