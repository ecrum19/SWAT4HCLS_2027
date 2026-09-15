# RQ2 — how the experiment works

> **Do the version-specific artifacts and alternative sample profiles behave as documented?**

---

## 1. Premise, and why the test is built this way

RQ1 shows that the vocabulary can express what VCF requires. It does this using
graphs built by the vocabulary repository's **own** materializer — a Python
script in the same repository that models vocabulary terms to specific fields of the VCF file using RDFLib graph objects.

That leaves an obvious hole. If the queries, the expected answers, and the graphs
all come from one codebase, a shared misunderstanding passes every test. The
result would mean *"this repository is internally consistent"*, which is not what
the paper wants to claim.

So RQ2 changes exactly one thing and holds everything else fixed:

- **Same** fixtures, **same** queries, **same** expected answers as RQ1
- **Different** program producing the RDF

The second program is VCF-RDFizer, which converts through RML mappings executed
by RMLStreamer rather than by building triples in Python. Where the two producers
agree, a claim about the vocabulary is supported by two independent
implementations. Where they disagree, something is wrong in at least one of them
and the interesting question is *which*.

> **An honesty note the paper also makes.** The two programs share an author.
> They share no code, so this catches implementation mistakes — but it is weaker
> than reproduction by an unrelated group, and should not be described as "truly"
> independent replication.

### Why the profile comparison is also considered

VCF Core offers two ways to store sample data: **expanded** (one resource per
sample and field) and **condensed** (vectors, for cohort-scale data). The
documentation claims these are alternatives, not a full and a reduced version.
Because every case already runs in both profiles, testing that claim costs
nothing extra — and it enables the claim to actually be tested.

---

## 2. The code, how it works, and what it tells us

### 2.1 Reproducible workflow for replicating results

The script `RQ2/run.sh` clones the vocabulary (`v2.1.2`) and the converter (`v3.0.3`)
from GitHub, pulls the converter's container image **by digest** so a moved tag
cannot change what executes, converts the fixtures, then runs four analyses.

Checkouts land in `.artifacts/<name>-<tag>/` at the repository root and are shared
with RQ1 and RQ3, so running all three fetches each repository once rather than
once per question. The tag is part of the directory name, so changing a pin
fetches a fresh checkout instead of reusing the previous one. Every pinned
artifact and digest is listed in [PINS.md](../PINS.md).

Every step is recorded in `RQ2/runs/<timestamp>/steps.jsonl` with its exit code and
duration, and its output in `logs/`.

### 2.2 Which fixtures are converted

**All 38 fixtures from RQ1**, in both profiles: 76 VCF-RDFizer generated witnesses (38 expanded and 38 condensed).

### 2.3 How one check is scored (`analysis/cross-producer.py`)

For each case × axis × profile:

1. Load the **materializer's** graph (from RQ1) and the **converter's** graph (from VCF-RDFizer).
2. Run the same query on both.
3. Compare each result against the expected answer written in advance.
4. Record one of four outcomes.

| Outcome | Meaning |
| --- | --- |
| `pass/pass` | Both producers answered correctly. |
| `pass/fail` | The materializer answered, the converter did not. **This is a divergence.** |
| `fail/fail` | Neither answered. Usually a documented profile trade-off. |
| `fail/pass` | The converter answered and the materializer did not. |

The expected answer is **never re-derived** — it is read from the reviewed
register (from RQ1). The RQ2 experiment adds a producer (VCF-RDFizer); it does not add an oracle.

### 2.4 The comparison rule, and its one real weakness

`normalize()` (`cross-producer.py:50`) compares answer *values*. For IRIs with a
fragment it keeps the fragment and discards the part before `#`, because the two
producers legitimately mint resource IRIs under different base IRIs.

> **Weakness worth knowing.** 360 of 5419 expected values are IRIs, and 292 of
> those have fragments, so they are compared by fragment alone. A converter that
> emitted `wrongnamespace#FloatType` would still pass. **This check cannot detect
> a namespace error.** It did not cause any of the divergences reported below —
> those all failed on missing properties — but the limitation is real.

### 2.5 Where the materializer's side comes from

The materializer's graph is **built during the run**, by calling the same
`materialize()` function RQ1 uses, on the same fixture, with the same base IRI.
So both sides of every comparison are produced by running a program, not by
reading a file someone committed earlier.

This was not always so. An earlier version read the recorded witness files in
`generated/witnesses/`, which meant comparing against a *record* of what the
materializer produces rather than against the materializer — and a stale record
would have gone unnoticed, quietly changing what the reported figures mean.

The committed witnesses are still used, but as a **check rather than an input**:
after building a graph the script compares it with the recorded witness and
**aborts** if they differ, naming the file and telling you to rebuild the
vocabulary's own assessment. Verified by deleting one triple from a witness: the
run stops with exit code 1 and that message, rather than reporting numbers from
mismatched inputs.

Switching from recorded to live graphs changed no result — 840 checks, the same
693 / 102 / 45 split, the same 15 divergent requirements — which is what should
happen when the records were current.

### 2.6 Other useful analyses

**`round-trip.py`** rebuilds VCF columns from the RDF alone and compares them
with the source file, to test that information survives the round trip through
structured properties rather than through a preserved raw string.

**What it compares.** Seven fixed columns — CHROM, POS, ID, REF, ALT, QUAL,
FILTER — plus the GT subfield of every sample column. Genotypes are rebuilt from
ordered `GenotypeAlleleCall` resources using `callIndex`, `calledAllele`,
`isNoCall` and the per-call `phaseIndicator`. The per-call indicator is what
allows a mixed genotype such as `0|1/2` to be reconstructed; a single
genotype-level phasing status could not express it.

> **One named normalisation, and why it is not a cheat.** VCF 4.4 onwards allows
> a leading phase indicator: `|0|1` and `0|1` describe the same phasing. The
> vocabulary treats that difference as lexical rather than semantic —
> `phaseIndicator` is defined as carrying "the effective first indicator when
> omitted in the source", and only `genotypeString` records whether it was
> written out. Since `genotypeString` is a preserved source string this check
> must not read, the leading character is not recoverable structurally. The
> comparison therefore removes it from the source genotype first. Allele order,
> missing calls, ploidy and every indicator between a pair must still match
> exactly.

> **One limit that remains.** The script binds alleles to records by **matching
> IRI text** — `STRSTARTS(STR(?a), CONCAT(STR(?r), "/allele/"))` — not by
> following a graph relationship, so it depends on the converter's IRI naming
> convention. It fails safe: a different layout yields empty REF/ALT and a
> reported mismatch, not a false pass.

**Verified falsifiable.** Flipping one `phaseIndicator` from `/` to `|`, and
separately deleting one allele call, each produce exactly one genotype mismatch.
A check that always passes would be worthless, so this was tested rather than
assumed.

**`field-round-trip.py`** does for INFO and the non-GT FORMAT subfields what
`round-trip.py` does for the fixed columns and GT: rebuilds each value from the
structured layer and compares it with the source. Together the two cover every
data value on every line. Verified falsifiable — corrupting one INFO value item
and deleting one FORMAT value each produce exactly one mismatch.

**`evidence-map.py`** maps requirements to research questions and audits the
assessment for duplicate checks. It is analysis of RQ1's shape, not a test.

**`profile-figures.py`** counts triples and distinct vocabulary terms the
converter emits for one worked example, and checks every emitted term is declared
in the cited release. Declaredness is checked against a **git tag**, not the
working tree, so an uncommitted edit cannot flatter the result.

### 2.7 Exclusions and thresholds actually in force

- **No sampling, no thresholds, no tolerances.** Every case that has a test is
  replayed; comparison is exact equality.
- A structure-axis query that decodes compound strings would be skipped, but **no
  query triggers this** — the rule never fires in practice.
- The round-trip runs on **expanded-profile graphs only**. Decoding a condensed
  vector needs a property the converter does not emit (requirement R21), so the
  condensed half cannot currently be tested.

---

## 3. Results, and how to read them

### 3.1 Cross-producer replay

**840 checks** — the same 840 query executions RQ1 performs, now performed once
per producer.

| Outcome | Checks |
| --- | ---: |
| Both producers pass | **693** |
| Materializer passes, converter does not | **102** |
| Both fail | 45 |
| Converter passes, materializer does not | 0 |

53 requirements exercised · 38 agree on every check · 32 pass on every check.

**How to read the 45 both-fail checks.** Every one is a condensed-profile
structure query. Both producers answer them the same way, and that way is "no" —
the documented storage trade-off, not a disagreement.

### 3.2 The 102 divergences: why the converter is silent

Fifteen requirements diverge. Each was examined individually by running the
failing query against both graphs and checking which properties the converter
actually emits.

| Cause | Reqs | What is missing |
| --- | ---: | --- |
| A declared property the converter never writes | **12** | The query asks for a property the vocabulary defines and the converter does not emit, so nothing matches. 20 such properties. |
| A decomposition that stops early | 1 | Tandem repeats: summary row emitted, per-allele components not. |
| A datatype the vocabulary leaves open | 1 | QUAL: `vcfc:VCFFloat` vs `xsd:decimal`. Both valid. |
| An encoding convention | 1 | Empty local-allele list written `""` by one producer, `"."` by the other. |

**The result that matters: none of the 15 is the vocabulary being unable to
express something.** All 20 absent properties are declared in `v2.1.2` — checked
against the tag. The converter simply does not write them yet.

**The result that bounds the claim:** twelve of fifteen are unfinished converter
work. With five divergences that was a footnote. With fifteen it is a real limit
on what can be said about the implementation, as opposed to the vocabulary.

### 3.3 Sample profiles

The profiles return the same outcome on **352 of 420** comparable checks. All 68
disagreements share one property: every one reads data held **inside a sample** —
a FORMAT value or a genotype. Questions about the file, its header, a record or
an allele agree on every check in both profiles.

**How to read this.** It is the trade-off working as designed. The condensed
profile stores sample values as vectors, so a query that descends into a sample
finds nothing to walk. The supported claim is therefore narrower than "the
profiles are equivalent": they agree above the sample level and diverge by design
below it.

### 3.4 Round-trip

Two checks together rebuild almost every value on a VCF data line from the
structured layer, and compare it with the source.

| Check | What it rebuilds | Result |
| --- | --- | ---: |
| `round-trip.py` | The seven fixed columns, and each sample's GT | **109/109** records, **151/151** genotypes |
| `field-round-trip.py` | Every header line | **431/431** lines |
| `field-round-trip.py` | Every INFO entry and every non-GT FORMAT subfield | **400/401** values |

```
CHROM  POS  ID  REF  ALT  QUAL  FILTER  INFO  FORMAT  SAMPLE1  SAMPLE2 …
└──────── round-trip (7 columns) ──────┘  └┬─┘        └───────┬───────┘
                                           └── field-round-trip ──┘
                                                (401 values)
```

**How to read this.** Information survives conversion into the structured layer
and can be read back out of it without touching a preserved source string. The
field check rebuilds a multi-valued field from its ordered value items and joins
them, recognises a flag by `fieldValueBoolean`, and otherwise reads the field's
own value. It never reads `infoRaw` or `sampleDataRaw`, the whole preserved
source columns, because that would make it trivial.

**The one failure is informative.** At position 4 of the local-allele fixture
`LAA` is an empty list — the source cell is `0/0::30:0`, so the field is present
and its value is empty. The converter emits a `FormatFieldValue` resource with a
`declaredBy` link and **no value at all**, so nothing can be read back. That is
requirement R27 from the cross-producer replay, reached independently by a
different route, which is some evidence that both checks measure something real.

**Header lines are covered too.** Each `##` line is recovered by its own source
line number and compared on both its key and its verbatim right-hand side, so the
header is reconstructed line for line, in order. All 431 across the 38 fixtures
match.

**Still out of scope:** byte-level details — how a structured header's attributes
are ordered inside the line, and the line terminators. The methodology
deliberately does not score attribute order, because VCF 4.4 and 4.5 state that
implementations must not rely on it. So this is not byte-for-byte file
reconstruction, but it is every header line and every data value bar one.

---

## Open issues

1. ~~The round-trip does not check genotypes, but says it does.~~ **Fixed.** It
   now compares all 151 sample genotypes; 151/151 recover. Fixing it also
   exposed a keying bug in the check itself: records and genotypes were keyed by
   position, so the local-allele fixture — which writes each site twice — merged
   two records' genotypes and produced `2/2/2/2` where the source said `2/2`.
   Both are now keyed by record identity.
2. **The round-trip and the RQ3 query both bind alleles by IRI text.** Fails safe,
   but it couples the check to one converter's naming convention.
3. ~~RQ2 assumes RQ1's committed witnesses are current without checking.~~
   **Fixed.** The materializer's side is built during the run, and the committed
   witness is now a freshness assertion that aborts on a mismatch (§2.5).
