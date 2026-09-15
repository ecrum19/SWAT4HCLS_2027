# RQ3 — how the experiment works

> **Does the resulting representation support a reproducible integration task while retaining source context?**

---

## 1. Premise, and why the test is built this way

RQ1 and RQ2 stay inside the VCF world: they ask whether information survives
conversion and whether two programs agree about it. Neither shows the
representation is *useful* — that someone can join it to external knowledge and
get a trustworthy answer.

RQ3 is one small end-to-end case study. It deliberately does **not** try to be a
realistic clinical workflow, because a large demonstration proves less: the more
moving parts, the harder it is to say which one produced the answer.

### The one difficulty it is built around

The case study turns on VCF 4.5 **local alleles**, chosen because a correct
answer is impossible without handling interpretation context properly.

In VCF, a `FORMAT` field declared `Number=R` normally has one value per allele:
the reference allele, then each alternate in the order the record lists them. But
`LAD` is declared `Number=LR`, which means one value per allele of **that
sample's own local allele subset**, named by its `LAA` field — not per entry of
the record's ALT column.

So answering *"how deep is this alteration in this sample?"* needs three things
at once:

1. the **declaration** (`Number=LR`, from the file header),
2. the sample's **`LAA` subset**, and
3. the allele's **position within that subset**.

Drop any one and the arithmetic still yields an answer — just the wrong one.

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

## 2. The code, and what to check before trusting it

### 2.1 What runs

`sh RQ3/run.sh`:

1. Clones the vocabulary (`v2.1.2`) and converter (`v3.0.3`) from GitHub, pulls
   the container image **by digest**.
2. Converts `local-alleles-v4.5.vcf` in the **expanded** profile.
3. Loads that graph together with `inputs/annotations.ttl`.
4. Runs `inputs/local-allele-evidence.rq`.
5. Compares the result with `inputs/expected.json`.

No local checkout of anything is needed.

**Why expanded only:** the query walks per-sample value resources. The condensed
profile stores those as vectors, so the query would find nothing — a profile
limitation (see RQ2 §3.3), not a result about local alleles.

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
3. **Provenance is present** — every returned row carries a source file IRI.

### 2.6 Weaknesses a reviewer should know

- **The provenance check is shallow.** It verifies the file IRI starts with
  `file://`, not that it names the *right* file. A converter emitting
  `file://wrong.vcf` would pass this check.
- **The query binds alleles by IRI text** —
  `STRSTARTS(STR(?altAllele), CONCAT(STR(?record), "/allele/"))` — rather than by
  following a graph relationship, so it depends on the converter's IRI naming
  convention. It fails safe: a different layout returns no rows, which fails
  loudly rather than passing wrongly. (Same pattern as RQ2's round-trip.)
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

---

## Open issues

1. **The "wrong answer" comparison is derived, not executed.** It would be
   stronger to run the query against output from a converter that reads
   `Number=LR` positionally and record both results. That needs a second
   converter version, which the current single-version design deliberately
   excludes — so this is a trade-off to confirm rather than a defect.
2. **The provenance check should verify the file identity**, not just the IRI
   scheme (§2.6). A one-line change.
