# RQ3 — how the experiment works

> **Does the materialized RDF representation support a reproducible integration task while retaining source context?**

---

## 1. Premise, and why the test is built this way

RQ1 and RQ2 stay inside the VCF world: they ask whether information survives
conversion and whether two programs agree about it. Neither shows the
representation is *useful* — that someone can join it to external knowledge and
get a trustworthy answer.

RQ3 is one small end-to-end case study. It deliberately does **not** try to be a
realistic clinical workflow, because a large demonstration proves less: the more
moving parts, the harder it is to say which one produced the answer.

### Why local alleles are worth caring about

Local alleles exist because of cohort sequencing. When thousands of samples are
called together, a single position accumulates every alternate allele seen in
*anyone* — while any individual usually carries one or two. Without local
alleles each sample must still carry a value for every allele at the site, and
genotype likelihoods grow quadratically: three values for two alleles, 210 for
twenty, 5050 for a hundred. Multiply that by a large cohort and the file becomes
impractical.

VCF 4.5's answer is to let each sample name the alleles that are actually
relevant to it, in `LAA`, and give its depths and likelihoods against that
shorter list. The saving is real, and so is the cost: the numbers in a sample's
column no longer line up with the record's ALT column.

The question this case study asks — *is this alteration actually supported by
reads in this sample?* — is the first one asked of any candidate variant, because
read depth is what separates a real observation from a sequencing artefact. Get
the allele mapping wrong in a local-allele file and you attribute one alteration's
read support to a different alteration at the same position. The depth you report
is a real number, measured from real reads; it simply belongs to the wrong
change. Nothing about it looks anomalous, which is why it would survive review.

The specification anticipates exactly this. Having set out the encoding, it
recommends that libraries *"provide an API in which local allele encoding can be
abstracted away from the API consumer and values accessed through their
corresponding non-local key"* — an acknowledgement that hand-decoding this is
error-prone and should be done once, properly, rather than by every consumer.
Representing it in the graph is the same argument by another route.

That is the motivation for choosing this difficulty. It is **not** a claim about
the data used below, which is synthetic and carries no biological meaning: the
fixture exists to make the failure mode observable, not to describe a genome.

### The one difficulty it is built around

A demonstration is only worth running if it could have come out wrong. This one
is built on the place where VCF 4.5 most readily leads a careful reader astray:
**local alleles**.

The difficulty is not that the data are hard to find. It is that the obvious
reading of them is wrong, and looks right.

A `FORMAT` field declared `Number=R` carries one value per allele of the record:
the reference first, then each alternate in the order the ALT column lists them.
Line up values against alleles and you have your answer. But `LAD` is declared
`Number=LR`, and that single extra letter moves the frame of reference. Its
values belong to the alleles of **that sample's own local subset**, named in the
sample's `LAA` field — a subset that may skip alternates the record declares, and
which differs from one sample to the next.

So answering *"how deep is this alteration in this sample?"* needs three things
at once:

1. the **declaration** (`Number=LR`, from the file header),
2. the sample's **`LAA` subset**, and
3. the allele's **position within that subset**.

Drop any one of the three and the arithmetic still completes. It simply lines up
the values against the wrong alleles, and reports a depth that belongs to
something else.

**That is the whole point.** A wrong implementation does not crash or return
nothing here. It returns the *same number of rows*, naming different alterations
at different depths. A test that compared row counts would pass both. This is why
the check compares identities and values, never counts.

### Why the annotations are synthetic and local

The external knowledge — five "flagged alterations" — is invented and labelled as
such in the file. It is stored locally rather than fetched from a live service so
the example gives the same answer on every run. **No biological or clinical claim
is made or intended.** The test is about whether the join and the interpretation
work, not about the biology.

---

## 2. The code, how it works, and what it tells us

### 2.1 Reproducible workflow for replicating results

```sh
sh RQ3/run.sh
```

One command, and it needs no local copy of anything: `git`, `docker`, and
`python3` with `rdflib`.

**1 — Fetch what is being evaluated.** The vocabulary is cloned at tag `v2.1.2`
and the converter at `v3.0.3`, into `.artifacts/` at the repository root, shared
with RQ1 and RQ2 so each is fetched once however many questions you run. The
converter's container image is pulled **by digest**
(`sha256:31f1361b…`) rather than by tag, so a tag moved later cannot silently
change what executes. The resolved commit of each is printed and recorded.

**2 — Convert the fixture.** `local-alleles-v4.5.vcf` is taken from the cloned
vocabulary — not from a copy in this directory, so it is the released fixture —
and converted in the **expanded** profile with compression and secondary
representations turned off, leaving plain N-Triples. The result is a graph of
roughly 1,400 triples describing one file, four sites written twice over, one
sample and its genotypes.

> **Why expanded only.** The query walks per-sample value resources: a sample
> call, its `LAD` field, that field's ordered value items. The condensed profile
> stores the same information as vectors instead, so those resources do not
> exist and the query would return nothing. That would be a fact about the
> profile (RQ2 §3.3), not about local alleles, so the case study avoids the
> confound by using one profile and saying so.

**3 — Assemble the graph to query.** `check.py` loads the converted graph and
[`inputs/annotations.ttl`](inputs/annotations.ttl) into a single in-memory graph.
This is the whole of the "integration": two independently produced sources of
statements, sharing no identifiers, placed side by side so that a query can try
to relate them.

**4 — Run the query.**
[`inputs/local-allele-evidence.rq`](inputs/local-allele-evidence.rq) joins the
two, applies the depth threshold, and projects the answer together with the
evidence for it — the source file, the sample, the field and the declaration that
gives the field its cardinality.

**5 — Compare with answers written beforehand.** The result is checked against
[`inputs/expected.json`](inputs/expected.json), on three conditions described in
§2.5: the rows match exactly, each excluded alteration is confirmed absent
individually, and every row's provenance names the converted fixture.

**What you are left with**, in `RQ3/results/`:

| | |
| --- | --- |
| `integration.json` | Observed rows, expected rows, the comparison, and the confirmed exclusions |
| `check.txt` | What the check printed |
| `local-alleles-v4.5.nt.gz` | The converted graph itself, ~12 KB, so the query can be re-run or varied without converting anything |
| `run.json` | Machine, toolchain versions, and the exact commits and image digest used |

Re-running reuses an existing conversion rather than repeating it, so iterating
on the query costs seconds. Delete `RQ3/work/` to force a clean conversion.

### 2.2 How the join is made

An annotation names an alteration by **four literals**: contig, position,
reference allele, alternate allele. The query matches those against the graph.

Nothing is pre-linked. There is no shared identifier minted in advance, so the
join rule is visible in the query text rather than hidden inside an IRI someone
generated earlier. That is deliberate: a pre-minted link would be assuming the
answer.

### 2.3 Assumptions the join rests on

Stated because they are what would break it:

- **Reference compatibility** — both sides are assumed to describe the same
  genome assembly. The snapshot records one; nothing checks it against the VCF's
  `##reference` line.
- **Alteration identity** — an alteration is its as-written REF/ALT pair at a
  position. No normalisation, no left-alignment, no VRS identifier. The join
  would not survive a differently written representation of the same change.
- **Sample identity** — `sample` is a VCF sample column. It is **not** a patient,
  and nothing here treats it as one.

### 2.4 Thresholds and exclusion criteria, stated explicitly

| Setting | Value | Where | Why |
| --- | --- | --- | --- |
| Depth threshold | `LAD >= 20` | query line 38 | Gives the question a definite answer. Chosen so that the correct reading and a positional misreading select *different* alterations. Not a clinical threshold. |
| Field restriction | `?fieldId = "LAD"` | query line 32 | The case study is about one `Number=LR` field. Other depth-like fields are out of scope. |
| Annotation restriction | `a ex:FlaggedAlteration` | query line 8 | Only the five flagged alterations are considered. |
| Profile | expanded only | `run.sh` | §2.1. |
| Fixture | one, 4 sites, 1 sample | `run.sh` | §3.3. |

### 2.5 How the comparison is made (`check.py`)

Three things must all hold for **PASS**:

1. **Rows match exactly** — the observed rows equal the expected rows across all
   eight fields (contig, position, ref, alt, depth, sample, fieldId, number). Not
   a count comparison.
2. **Every excluded alteration is absent by identity** — each of the three
   flagged-but-excluded alterations is checked individually. Absence must be for
   the stated reason, not because the query returned nothing.
3. **Provenance identifies the right file** — every returned row must cite a
   source file whose IRI names the fixture that was actually converted, and all
   rows must cite the same one. The fixture name comes from the path the check
   was given, so the anchor is outside the graph: a graph cannot satisfy this by
   being internally consistent.

### 2.6 Weaknesses a reviewer should know

- **`excludedConfirmed` in the output lists all excluded rows unconditionally.**
  In a PASS run that is accurate, because a returned exclusion would have made
  the run FAIL. In a FAIL run the field would be misleading.
- **Depth is compared as text**, so `"30"` and `"30.0"` would differ. Consistent
  in practice, but it is a lexical comparison, not numeric.

---

## 3. Results, and how to read them

### 3.1 The answer

**PASS** — two rows, exactly matching the answers authored in advance:

| Alteration | Depth | Sample | Via |
| --- | ---: | --- | --- |
| chr1:1 G>C | 30 | `sample` | `LAD` declared `Number=LR` |
| chr1:2 A>T | 25 | `sample` | `LAD` declared `Number=LR` |

Three flagged alterations were correctly **not** returned, each confirmed absent
individually:

| Excluded | Why |
| --- | --- |
| chr1:1 G>A | ALT 1 is not in `LAA=2,4`; this sample reports no depth for it |
| chr1:2 A>C | ALT 1 is not in `LAA=3` |
| chr1:3 C>G | ALT 1 is not in `LAA=3`, and its positional value would be 1 — below threshold either way |

### 3.2 Why this is more than "a query returned rows"

Read `Number=LR` positionally — taking the *n*th `LAD` value as belonging to the
*n*th ALT allele — and the query returns **two rows again**: `chr1:1 G>A` at
depth 30 and `chr1:2 A>C` at 25.

Those alterations and depths are written down in `expected.json` **as the
positional-reading outcome**, derived from the fixture text before the query was
ever run. So:

- Same row count.
- Different alterations.
- Full provenance attached to the wrong answer.

A count-based check cannot tell the two apart. That is the concrete argument for
why the declaration, the local allele set and the allele ordinal have to be
*represented* rather than inferred.

> **Scope of this claim.** The wrong rows are derived from the specification
> rule, not measured by running an incorrect converter. The prediction is
> recorded in the committed expected answers; it is reasoning about what a
> positional reading yields, not an executed comparison.

### 3.3 What this does not show

- The input is **synthetic and tiny**: four sites, one sample.
- The annotations are **invented**. Nothing here is a biological finding.
- The join assumes as-written allele identity, so it says nothing about matching
  normalised or VRS-identified variation.
- One fixture shows local alleles resolve correctly **here**, not in general.
- No performance or scale claim follows from it.
