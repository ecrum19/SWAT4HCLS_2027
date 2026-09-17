# Reproducing the paper's results

Every experimental figure in the paper comes from one command:

```sh
sh RQ2/run.sh
```

It needs `git`, `docker` and `python3` with `rdflib`, about 2 GB of disk and
around ten minutes. Everything it evaluates — the vocabulary, the converter, the
container image — is fetched at a pinned revision or digest, so the result does
not depend on the machine it runs on.

## What is here

| | |
| --- | --- |
| [`run.sh`](run.sh) | The whole pipeline. Pinned versions are the first thing in the file. |
| [`summarise.py`](summarise.py) | Turns one run directory into the numbers the paper quotes. |
| [`analysis/`](analysis) | The four checks, described below. |
| [`runs/`](runs) | Completed runs. The paper cites the most recent. |

## What each run records

A run writes one self-contained directory under `runs/`, named by UTC timestamp:

| | |
| --- | --- |
| `env.json` | The machine, the toolchain versions, and exactly what was pinned — including the specification revisions with their SHA-256 digests and the container image digest. |
| `steps.jsonl` | Every command executed, with its exit code and duration. |
| `logs/` | Standard output and error of each step. |
| `graphs/` | The converted RDF each result was computed from. |
| `results/` | The JSON each check wrote. |
| `SUMMARY.md` | The headline numbers. Start here. |

## The four checks

**`cross-producer.py`** re-executes the vocabulary's own specification-derived
assessment over graphs the converter produced. The queries and expected answers
are not re-derived: it reuses the reviewed ones from the vocabulary repository,
and reports where the two producers agree. This is what distinguishes *the
vocabulary can express this* from *the software people use does*.

**`round-trip.py`** rebuilds CHROM, POS, ID, REF, ALT, QUAL, FILTER and the
genotype from the RDF alone and compares them with the source VCF. Recovery is
structural — alleles come from ordered allele resources, genotypes from ordered
call resources — so no untouched source string can serve as a shortcut.

**`evidence-map.py`** maps the assessment's requirements to the paper's research
questions and comparison features, and audits it for duplicate checks.

**`profile-figures.py`** counts the triples and distinct vocabulary terms the
converter emits for the paper's worked example, in both sample profiles, and
verifies that every emitted term is declared in the cited vocabulary release.

The integration case study that used to live here is now [`RQ3/`](../RQ3/README.md),
which answers a different research question and runs on its own.

## Scope

The fixtures are small and synthetic by design: they exercise particular
specification requirements, not realistic data volumes. Nothing here measures
conversion throughput, and no annotation in the integration example carries
biological or clinical meaning.

