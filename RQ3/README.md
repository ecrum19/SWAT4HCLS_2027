# RQ3 — does the representation support a reproducible integration task while retaining source context?

One end-to-end case study, bounded to a single difficulty, answered with
answers written down before the query was run.

```sh
sh RQ3/run.sh
```

Needs `git`, `docker` and `python3` with `rdflib`. No local checkout of anything:
the vocabulary and the converter are cloned from GitHub at pinned tags and the
container image is pulled by digest. Output lands in `results/`.

## The question the case study asks

> Which sample observations correspond to flagged alterations with supporting
> read depth of at least 20, and what source evidence supports them?

Answering it requires three things at once, which is the point. `LAD` is
declared `Number=LR`: one value per allele of **the sample's own local allele
subset**, named by `LAA`, not per entry of the record's ALT column. So a
consumer needs the declaration, the sample's `LAA`, and the allele's ordinal
together. Drop any one and the arithmetic still produces an answer — just the
wrong one.

## Inputs

| | |
| --- | --- |
| VCF | `coverage/methodology/fixtures/local-alleles-v4.5.vcf`, from the pinned vocabulary release. Four sites, one sample, each site written twice — once with `LAA`/`LAD`/`LPL` and once with the equivalent global `AD`/`PL`. |
| [`inputs/annotations.ttl`](inputs/annotations.ttl) | Five flagged alterations. **Entirely synthetic and labelled as such in the file.** Local rather than federated so the example returns the same answer on every run. |
| [`inputs/local-allele-evidence.rq`](inputs/local-allele-evidence.rq) | The query. The annotation-to-record join is written out in it — four literals: contig, position, REF, ALT — rather than hidden inside a pre-minted identifier. |
| [`inputs/expected.json`](inputs/expected.json) | The answers, derived from the VCF text and the `Number=LR` rule **before the query was run**, never from converter output. Each row records why it is expected; each exclusion records why it is absent. |

## The three assumptions the link rests on

Stated because they are what would break it:

- **Reference compatibility.** Both sides are assumed to describe the same
  assembly. The snapshot records one; nothing checks it against `##reference`.
- **Alteration identity.** An alteration is its as-written REF/ALT pair at a
  position. No normalisation, no left-alignment, no VRS identifier — so this
  link would not survive a differently written representation of the same change.
- **Sample identity.** `sample` is a VCF sample column. It is **not** a patient,
  and nothing here treats it as one.

## What makes the answer discriminating

A positional reading of `Number=LR` — taking the *n*th `LAD` value as belonging
to the *n*th ALT allele rather than to the *n*th member of the sample's `LAA`
subset — returns **the same number of rows**, naming different alterations at
different depths. `expected.json` records those wrong rows and their depths
alongside the right ones, so a reader can see that a check comparing result
counts would pass either way.

That is the concrete form of the paper's argument: retaining the declaration,
the local allele set and the allele ordinal is not bookkeeping, because dropping
it yields a plausible, well-formed, wrong answer delivered with full provenance.

## Limits

The input is synthetic and tiny — four sites, one sample. The annotations are
invented and carry no biological or clinical meaning; nothing here is a finding.
The link assumes as-written allele identity, so it says nothing about matching
normalised or VRS-identified variation. And a single fixture establishes that
the converter resolves local alleles correctly *here*, not in general.
