# W4 — Integration example

Executed 2026-09-13 on the `vcf-bench-2` VM. Scripts and results: [`w4/`](w4/).

`VCF input → VCF Core 2.1.1 graph → flagged alterations → SPARQL → checked answers with provenance`

## W4.1 What the example is bounded to

One difficulty: **allele-dependent values under VCF 4.5 local alleles**, with source
provenance as the closely related second.

`LAD` is declared `Number=LR` — one value per allele of *the sample's own* local allele
subset, named by `LAA`, not per entry of the record's ALT column. Answering "how deep is
this alteration in this sample?" therefore needs three things at once: the declaration's
`Number`, the sample's `LAA`, and the allele's ordinal. That is the interpretation context
the manuscript argues VCF Core preserves, in the smallest case that actually requires it.

It was chosen because the expected answer **depends on handling it correctly** — see W4.5,
where the same query over a converter that resolved `Number=LR` positionally returns the
same number of rows describing different alterations.

## W4.2 Inputs

| | |
| --- | --- |
| VCF | `coverage/methodology/fixtures/local-alleles-v4.5.vcf` (vcf-core-vocabulary `v2.1.1`, unchanged in `v2.1.2`) |
| Provenance | **Authored, not observed.** A synthetic fixture written to exercise the VCF 4.5 local-allele families. |
| Size | 4 sites, 1 sample, 8 data lines — each site written twice, once with `LAA`/`LAD`/`LPL` and once with the equivalent global `AD`/`PL` |
| Converter | VCF-RDFizer `fix/vcf45-structured-accessors` (`e128c71`), expanded profile; that branch was released as `v3.0.3` (`be658a2`) on 2026-09-14 |
| Annotations | [`w4/annotations.ttl`](w4/annotations.ttl) — pinned local snapshot, five flagged alterations |

The annotation snapshot is **entirely synthetic and labelled as such in the file**. No
clinical or biological claim is made. It is local rather than federated because the example
must give the same answer on rerun, which a changeable remote resource cannot promise.

## W4.3 The integration link, and its assumptions

An annotation names an alteration by four literals — contig, position, reference allele,
alternate allele — and the query joins on them. Nothing is pre-linked, so the mapping rule
is readable in [`w4/local-allele-evidence.rq`](w4/local-allele-evidence.rq) rather than
hidden inside a minted IRI.

Three assumptions, stated because they are the ones that would break the link:

- **Reference compatibility.** Both sides are assumed to describe the same assembly. The
  snapshot records `ex:assembly`; nothing checks it against the VCF's `##reference`.
- **Alteration identity.** An alteration is its as-written REF/ALT pair at a position. No
  normalisation, left-alignment or VRS identifier is involved, so this link would not
  survive a differently-written representation of the same change.
- **Sample identity.** `sample` is a VCF sample column. It is **not** a patient, and nothing
  here treats it as one.

## W4.4–W4.5 Query, expected answers, observed answers

Question: *which sample observations correspond to a flagged alteration with read depth ≥ 20,
and what source evidence supports them?*

Expected rows were authored in [`w4/expected.json`](w4/expected.json) by reading the VCF text
and the `Number=LR` rule, **before the query was run**, and never from converter output.

**Observed: PASS — 2 rows, identical to the authored answers.**

| contig:pos | alteration | depth | sample | via | source file |
| --- | --- | ---: | --- | --- | --- |
| chr1:1 | G>C | 30 | `sample` | `LAD` `Number=LR` | `file://local-alleles-v4.5.vcf` |
| chr1:2 | A>T | 25 | `sample` | `LAD` `Number=LR` | `file://local-alleles-v4.5.vcf` |

Every row traces back to its file, record, sample and the FORMAT declaration that gives the
field its cardinality. The check compares identities, values and provenance — not row counts.

### The three excluded alterations

All three are flagged in the snapshot and absent from the answer, each for a stated reason:

| Excluded | Why |
| --- | --- |
| chr1:1 G>A | ALT 1 is not in `LAA=2,4`; this sample reports no depth for it |
| chr1:2 A>C | ALT 1 is not in `LAA=3` |
| chr1:3 C>G | ALT 1 is not in `LAA=3`; and its positional value would be 1, below threshold either way |

### Why the answer depends on the modelling choice

The same query and the same annotations, over a graph from the converter **before** the
local-allele fix (`e4de9d0`):

| | Correct | Pre-fix |
| --- | --- | --- |
| Row 1 | chr1:1 **G>C** @30 | chr1:1 **G>A** @30 |
| Row 2 | chr1:2 **A>T** @25 | chr1:2 **A>C** @25 |

Two rows either way. The count matches; the alterations do not. The pre-fix converter bound
`Number=LR` items to ALT positions, so it handed each depth to the wrong allele — and the two
alterations it wrongly reported are exactly the two `expected.json` predicted, at exactly the
predicted depths.

A check that compared result counts would have passed both graphs. That is the concrete
argument for the manuscript's claim: retaining the declaration, the local allele set and the
allele ordinal is not bookkeeping — drop it and a plausible, well-formed, wrong answer comes
back with full provenance attached.

## W4.6 Reproduction and limitations

```sh
sh w4/run.sh <vcf-core-vocabulary checkout> <VCF-RDFizer checkout> <workdir>
```

Converts the fixture and checks the query against the authored answers; exits non-zero if
they differ. Needs Docker and `rdflib`. Results land in `w4/generated/w4-results.json`.

**What this demonstrates:** that the representation carries the interpretation context, that
the mapping rule connects it to an external annotation, and that the answers are the ones
authored in advance.

**What it does not.** The input is synthetic and tiny — four sites, one sample. The
annotations are invented; nothing here is a clinical finding, and no performance or
cohort-scale claim follows. The link assumes a shared assembly and as-written allele
identity, so it says nothing about matching normalised or VRS-identified variation. And a
single fixture cannot establish that the converter resolves local alleles correctly in
general — it establishes that it does so here, where a previous release did not.
