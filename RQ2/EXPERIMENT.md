# RQ2 — how the experiment works

> **Do the version-specific artifacts and alternative sample profiles behave as documented?**

---

## 1. Premise, and why the test is built this way

RQ1 shows that the vocabulary can express what VCF requires. It does this using
graphs built by the vocabulary repository's **own** materializer — a Python
script in the same repository as the vocabulary, written by the same people.

That leaves an obvious hole. If the queries, the expected answers and the graphs
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
> than reproduction by an unrelated group, and should not be described as
> independent replication.

### Why the profile comparison rides along

VCF Core offers two ways to store sample data: **expanded** (one resource per
sample and field) and **condensed** (vectors, for cohort-scale data). The
documentation claims these are alternatives, not a full and a reduced version.
Because every case already runs in both profiles, testing that claim costs
nothing extra — and it is the only place the claim is actually checked.

---

## 2. The code, and what to check before trusting it

### 2.1 What runs

`sh RQ2/run.sh` clones the vocabulary (`v2.1.2`) and the converter (`v3.0.3`)
from GitHub, pulls the converter's container image **by digest** so a moved tag
cannot change what executes, converts the fixtures, then runs four analyses.

Every step is recorded in `runs/<timestamp>/steps.jsonl` with its exit code and
duration, and its output in `logs/`.

### 2.2 Which fixtures — and why this used to be wrong

**All 38 fixtures the assessment refers to**, in both profiles: 76 conversions.

The fixture list is **not written down**. `run.sh` derives it at run time from
the assessment's own case register, so a fixture added upstream is included
automatically.

> **This is a correction, not a feature.** An earlier version of this experiment
> carried a hand-written list of ten fixtures. It covered 143 of 210 cases and 39
> of the 53 requirements that have tests — and nothing in the reported numbers
> revealed that the other 28 fixtures had been skipped. Widening to all 38 raised
> the divergent-requirement count from 5 to 15. Ten real disagreements were
> hidden by the narrow list. The derived list exists so that cannot recur.

### 2.3 How one check is scored (`analysis/cross-producer.py`)

For each case × axis × profile:

1. Load the **materializer's** graph and the **converter's** graph.
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
register. This experiment adds a producer; it does not add an oracle.

### 2.4 The comparison rule, and its one real weakness

`normalize()` (`cross-producer.py:50`) compares answer *values*. For IRIs with a
fragment it keeps the fragment and discards the part before `#`, because the two
producers legitimately mint resource IRIs under different bases.

> **Weakness worth knowing.** 360 of 5419 expected values are IRIs, and 292 of
> those have fragments, so they are compared by fragment alone. A converter that
> emitted `wrongnamespace#FloatType` would still pass. **This check cannot detect
> a namespace error.** It did not cause any of the divergences reported below —
> those all failed on missing properties — but the limitation is real.
>
> The script's docstring claims *"every expected answer in cases.json is made of
> literals."* That is **incorrect**; 7% are IRIs. The code is right, the comment
> is wrong.

### 2.5 One assumption the script makes silently

The materializer side is read from **committed** witness files in the vocabulary
repository, not re-materialized during the run. If those files were stale, the
comparison would be against out-of-date data and nothing here would notice.

They are current — verified by re-materializing five fixtures in both profiles
and comparing — and RQ1's `assess.py check` detects staleness. But **RQ2 does not
verify it**, and relies on RQ1 having been run.

### 2.6 The other three analyses

**`round-trip.py`** rebuilds VCF columns from the RDF alone and compares them
with the source file, to test that information survives the round trip through
structured properties rather than through a preserved raw string.

> **Two limits, one of them a discrepancy you should act on.**
>
> - The script binds alleles to records by **matching IRI text** —
>   `STRSTARTS(STR(?a), CONCAT(STR(?r), "/allele/"))` — not by following a graph
>   relationship. It therefore depends on the converter's IRI naming convention.
>   It fails safe (a different layout yields empty REF/ALT and a reported
>   mismatch, not a false pass), but it is not a structural test.
> - **The genotype is reconstructed and then never compared.** `calls` is built
>   from the GT query and used only to count groups. The comparison covers seven
>   fixed columns: CHROM, POS, ID, REF, ALT, QUAL, FILTER. The script's own scope
>   string and the manuscript both say GT is included. **It is not.** See Open
>   issues.

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

**109/109 records** recovered — every data line across all 38 fixtures.

**How to read this.** It covers the seven fixed columns only (§2.6). It is not
whole-file reconstruction: INFO and the non-GT FORMAT subfields are out of scope,
and — contrary to the current wording — genotypes are not compared either.

---

## Open issues

1. **The round-trip does not check genotypes, but says it does.** `round-trip.py`
   builds the genotype and never compares it; the manuscript and the script's own
   scope string both claim GT is recovered. Either compare it (the data is
   already queried — this is a small change) or remove GT from the stated scope.
   **Until one of those happens, the paper overstates this result.**
2. **The round-trip and the RQ3 query both bind alleles by IRI text.** Fails safe,
   but it couples the check to one converter's naming convention.
3. **`cross-producer.py`'s docstring contradicts the data** about expected answers
   being all literals (§2.4).
4. **RQ2 assumes RQ1's committed witnesses are current** without checking (§2.5).
   A freshness assertion would close this.
