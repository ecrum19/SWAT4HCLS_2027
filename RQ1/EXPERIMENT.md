# RQ1 — how the experiment works

> **Does VCF Core preserve the intended meaning of the VCF constructs it claims to support?**

Two separate tests answer this, from opposite directions. Read §1 for why, §2 for
how the code works and where it could mislead you, §3 for what the numbers mean.

---

## 1. Premise, and why the tests are built this way

A vocabulary can fail at meaning in two different ways, and one test cannot catch both.

**It can be missing something.** If VCF says a field has one value per alternate
allele, and the vocabulary has no way to say which allele a value belongs to,
then a graph built with it has lost the meaning even though every character of
the file survived. Catching this needs a list of what VCF *requires*, written
from the specification without looking at the vocabulary — otherwise you only
ever find the gaps you already knew about.

**It can have the term but fail to use it correctly.** A vocabulary can declare
everything and still produce graphs where the question cannot actually be
answered. Catching this needs *executed queries*, not a term inventory.

So:

| Test | Direction | Guards against |
| --- | --- | --- |
| **Specification-derived assessment** (`methodology/`) | specification → vocabulary | Gaps the maintainers did not think of |
| **Curated construct inventory** (`vcf45-inventory/`) | vocabulary → specification | Terms that exist but are never exercised |

The first is the stronger evidence and is the one the paper leans on. The second
is a completeness map authored by the vocabulary's own maintainers, and it can
only cover what its authors thought to list — so it is reported separately and
never added to the first.

### Two design choices that make the result mean something

**Expected answers are written before the query runs.** Each test case pairs a
SPARQL query with the answer rows a reader of the specification says it should
return. Those rows come from reading the VCF text and the fixture, never from
running anything.

**Every test must be capable of failing.** Two automatic controls enforce this,
described in §2.5. Without them, a query that returns a constant would "pass".

---

## 2. The code, and what to check before trusting it

### 2.1 The words this section uses

Six terms do most of the work. They are easy to confuse because several sound
like plain English but mean something narrow here.

**Requirement** — one thing the VCF specification requires, rewritten as a
question that has a checkable answer. *"Can `Number=A` values be associated with
the correct ALT allele?"* is requirement R16. Each is anchored to the exact
passage it came from, by line range and SHA-256 of the pinned specification file.
There are **94**, spanning VCF 4.1–4.5. A requirement is a claim about VCF, not
about the vocabulary — it is written from the specification, so it can name
something the vocabulary turns out not to support.

**Fixture** — a small, hand-written `.vcf` file that exercises a requirement. A
VCF file is header lines beginning `##`, then a column-header line beginning
`#CHROM`, then one **record** per remaining line: a single variant site, giving
its position, its reference and alternate alleles, and one column of values per
sample. `basic-v4.1.vcf` holds three such records; `boundaries-v4.5.vcf` holds
thirteen. Fixtures are deliberately tiny and synthetic — each exists to make one
behaviour observable, not to resemble real data. There are **38**, and they are
the *only* input to graph construction.

**Case** — a requirement, tested at one VCF version, against one fixture. R16 is
one requirement but five cases, one per version. There are **210**. A case is
what carries a query and an expected answer; it is the unit that gets scored.

**Query** — the SPARQL that tries to retrieve the answer from the graph. Stored
in `queries/`, named by the case. One query is often shared by several cases.

**Expected answer** — the rows that query *should* return, written down by a
person reading the specification and the fixture, **before the query is run**.
This is the oracle: correctness is defined here, not by the query and not by the
graph. If a query is badly written it returns the wrong rows and the case fails.

**Witness** — the RDF graph built from a fixture, against which the query runs.
Also called a materialised graph. One per (fixture, profile) pair, so 76 in
total; they are written to `generated/witnesses/` as a record of what was
actually queried.

Two more that describe *how* a thing is tested rather than *what*:

**Profile** — which of the vocabulary's two sample encodings the graph uses.
**Expanded** gives each sample's value its own resource. **Condensed** packs
sample values into vectors, for cohort-scale data. Every case is tested in both.

**Axis** — which standard of evidence the case is judged by: whether the
information is retrievable *at all* (preservation), or retrievable *as graph
structure* (structure). §2.3 works through an example, because this is the one
that most often gets misread.

And four words used for outcomes:

| Outcome | Meaning |
| --- | --- |
| **demonstrated** | Every case for that requirement/version/profile passed. |
| **partial** | Some passed, some did not. |
| **not-demonstrated** | Cases exist and none passed. |
| **unassessed** | No test has been written yet. **Counts against the score**, rather than being excluded from it. |

### 2.2 What runs

`sh RQ1/run.sh` clones the vocabulary from GitHub at tag `v2.1.2`, then runs
three scripts **inside that cloned repository**:

| Script | What it does |
| --- | --- |
| `methodology/scripts/assess.py check` | The specification-derived assessment (`methodology/`) |
| `vcf45-inventory/report.py` | The construct inventory (`vcf45-inventory/`) |
| `vcf45-inventory/check_serialization.py` | Byte-level source rules, reported separately |

**It runs the clone, not the copies in this directory.** `assess.py` identifies
its inputs by their path *relative to the repository root* and the recorded
review decisions are tied to those identities, so running the copies from a
different location would report every requirement as unreviewed — an artefact of
where files sit, not a finding. `run.sh` first compares all 138 copied files
against the tag and refuses to run if any has drifted.

### 2.3 The two axes, with a worked example

Every requirement is tested **twice against the same graph**, once per axis. The
difference is not the question but the rule about what counts as an acceptable
way to reach the answer.

| Axis | The question | The query may… |
| --- | --- | --- |
| **preservation** | Is the information still there at all? | do anything, including pulling apart a packed string |
| **structure** | Is it there *as graph structure*? | **not** use `REPLACE`, `SUBSTR`, `STRBEFORE` or `STRAFTER` |

**A worked example.** Requirement R18 asks whether sample identity, field
identity, and read depth can be recovered together. In the condensed profile the
two axes use different queries.

*Preservation* reaches the packed vector and digs the value out with a regular
expression:

```sparql
?vectorvalue vcfc:declaredBy/vcfc:fieldId "DP" ; vcfc:encodedValues ?packedvalue .
BIND(CONCAT("^(?:[^\t]*\t){", STR(?sampleIndex - 1), "}([^\t]*).*$") AS ?pattern)
BIND(REPLACE(?packedvalue, ?pattern, "$1") AS ?value)
```

It **passes** — the depth genuinely is in the graph. *Structure* has to follow
relationships instead:

```sparql
?r vcfc:hasCall/vcfc:hasSampleCall ?s .
?s vcfc:forSample/vcfc:sampleName ?name ; vcfc:hasFormatValue ?v .
?v vcfc:declaredBy/vcfc:fieldId "DP" ; vcfc:fieldValue ?value
```

The condensed profile has no per-sample resources to walk, so this returns
nothing and **fails**. Same graph, same question: one axis says the information
survived, the other says it survived only as characters inside a string.

**Why this distinction earns its place.** Without it, a vocabulary that dumped
each VCF line into a single literal would score 100% on preservation — the
outcome the paper argues against. It is also the only reason the condensed column
is lower than the expanded one in §3.1.

45 of the 210 cases use genuinely different queries per axis. The other 165 use
the same query for both, which is why the 840 executions collapse to 465 distinct
ones (§3.4).

### 2.4 How one case is scored, step by step

Each case is scored once per profile and once per axis — up to four results.
Every step below carries assumptions, and those are what decide whether the
result means anything.

#### Step 1 — Build a graph from the fixture

`materialize(fixture, profile, base)` in `scripts/vcf_examples.py` (408 lines)
reads the VCF as text and builds an in-memory RDF graph. It is not a converter
and does not claim to be: its own first line is *"Materialize the repository's
explicit VCF fixtures; not a production converter."*

**How it works.** It splits the file into header lines and data lines, parses
each `##INFO=<...>`/`##FORMAT=<...>` declaration into a definition, then walks
each data row emitting resources for the file, header, records, alleles, samples,
genotypes and field values. Resource IRIs are minted under a base derived from
the filename, so nothing depends on where the file sits. No reference genome and
no remote ontology is fetched; everything comes from the fixture text.

**The property that makes this trustworthy: it fails instead of guessing.**
There are **16 points where it raises an error** rather than emitting something
approximate. The important ones:

| It refuses to continue when… | Why that matters |
| --- | --- |
| an INFO or FORMAT key is used in data but never declared in the header | A converter that silently skipped it would produce a smaller graph and the query would fail for the wrong reason |
| CHROM is neither a declared contig nor a bracketed assembly contig | Prevents inventing a reference |
| a sample row has the wrong number of tab-delimited columns | Prevents silent column drift |
| a structured header has unbalanced quotes or brackets, or duplicate attributes | Prevents a half-parsed declaration |
| a base-modification key is outside the known alias table | Prevents guessing a ChEBI identifier |

So the failure mode is a **crashed run**, not a quietly incomplete graph. That is
the single most important design property in step 1.

**Verified, not assumed.** Across all 38 fixtures, every INFO and FORMAT key that
is both declared and used reaches the graph as a `vcfc:fieldId`. Nothing declared
and used is dropped.

> **The assumption that could taint everything.** The materializer, the
> vocabulary and the queries were written by the same people. If the materializer
> emits exactly the shape the queries look for, a case passes whether or not the
> shape reflects what VCF actually means. Nothing inside RQ1 fully rules this out.
>
> Three things reduce it, and one removes it:
>
> - **Expected answers come from the specification**, not the graph, so a wrong
>   *value* is caught even if the shape is agreed between materializer and query.
> - **The materializer emits far more than the tests consult.** Across all
>   fixtures it emits **200 distinct vocabulary terms** while the 79 queries
>   reference **125** — **81 terms are emitted that no query ever asks for.** It
>   is modelling the format, not painting the target around the arrow.
> - **The two controls in §2.5** reject queries that pass without data.
> - **RQ2 removes it.** A second, independently written producer must answer the
>   same queries. That, not anything in RQ1, is what makes a shared misreading
>   detectable.

#### Step 2 — Run the query

The case names a query file per profile and axis, read from
`coverage/methodology/queries/`. It is run with rdflib's SPARQL engine against
the graph from step 1. There is no timeout, no result limit and no sampling:
**no query uses `LIMIT`**, so nothing depends on which rows come back first.

**Where the queries came from.** The pipeline is documented in the methodology
README — pinned specification text → authored source assertions → requirements →
fixtures → queries versus independent answers — and follows SAMOD (Peroni 2016),
which pairs a question, a witness, a query and separately authored answers. Each
requirement anchors to its specification passage by line range and SHA-256, and
61 of the 94 carry a `testPlan` saying what a test should exercise. Two rules are
machine-enforced: a structure-axis query may not decode compound strings, and a
passing query must survive both controls in §2.5.

> **But there is no authoring procedure for the queries themselves.** No README
> in `queries/`, no rule for turning a requirement into a particular SPARQL
> pattern. The recorded reasoning is thinner than the `testPlan` count suggests:
> of 94 `interpretation` fields only 58 are distinct, and 29 are the same
> boilerplate. The review also weighted them lightly on purpose — for each case
> it asks whether the *expected answer* follows from the source, while "reused
> query code needs reading once". Upstream, the source interpretations were
> AI-authored, which the README discloses, then human-reviewed.
>
> **What limits the damage:** the query is not the oracle. Correctness is defined
> by the expected answer, authored from specification text and checked case by
> case, so a badly written query fails rather than passes. The practical cost is
> that someone re-deriving these tests would write different SPARQL with no
> recorded rationale to compare against.

#### Step 3 — Compare with the answer written in advance

`answers()` (`assess.py:50`) converts every result row to strings and **sorts
both sides** before comparing. Its own comment states the rule: *"Compare bags,
not sets: extra rows and duplicate answers also fail the case."*

So the comparison is a **multiset**: an extra row fails, a missing row fails, a
duplicated row fails — but **the order rows come back in is not compared.**

> **Why discarding row order is safe here, and how it is handled.** Several
> requirements are explicitly about order — R07 asks whether records can be
> retrieved *in source order*. Those are not tested by row sequence. They project
> the ordinal as a **value**: R07's query selects `?i ?pos` where `?i` is
> `vcfc:recordIndex`, and its expected answer is
> `[['1','10'], ['2','20'], ['3','30']]`. A wrong index changes a value, and the
> multiset comparison catches it. Order is tested as data, which is the right
> way round — it does not depend on the query engine's iteration order.
>
> 22 of the 79 queries carry an `ORDER BY`. Since results are sorted afterwards
> and no query uses `LIMIT`, those clauses have **no effect on the outcome**.
> They are readability, not semantics.

#### Step 4 — Decide

**Pass** only if the two multisets are equal: same rows, same values, same
multiplicities. No partial credit, no tolerance, no numeric comparison — every
value is compared as a string, so `30` and `30.0` are different answers.

**Then the result is aggregated** by `status()` (§2.6), which requires *every*
case for a requirement/version/profile to pass before it counts as demonstrated.

### 2.5 The two controls that stop a test passing for the wrong reason

Both are in `run_query()` (`assess.py:55`). Both *raise an error* rather than
quietly recording a weaker result — a test that cannot fail is treated as a
broken test, not as a pass.

**Empty-graph control.** The query is run against a graph with nothing in it. If
it still returns the expected answer, the case is rejected. This catches queries
whose answer is baked into the query text.

**Predicate-deletion control.** For a passing query, each vocabulary property the
query mentions is deleted from the graph in turn. At least one deletion must
change the answer, or the case is rejected. This catches queries that appear to
test a property but do not actually depend on it.

> **Read this limit carefully.** The deletion loop stops at the *first* property
> whose removal changes the answer. So it proves the query depends on **some**
> vocabulary data — not that it depends on every property it names. The code says
> so itself: *"This checks data dependence; it is not a semantic proof."*

### 2.6 Scoring rule, stated plainly

`status()` (`assess.py:41`) gives **no fractional credit** and **never drops an
untested requirement from the denominator**. A requirement with no test scores
zero rather than being excluded. This is why the headline percentages look low:
they are a floor, not a ceiling.

### 2.7 Exclusions and thresholds actually in force

- **Structure-axis string-decoding ban** (§2.3). Enforced by raising an error.
- **Version gating.** A case is rejected unless its fixture's `##fileformat`
  line matches the version the case claims (`assess.py:173`).
- **Untested requirements are included** in every denominator. This is the
  opposite of an exclusion and is the single most important scoring decision.
- **Row order is not compared** (§2.4, step 3). Ordering requirements project the
  ordinal as a value instead.
- **All values are compared as strings.** `30` and `30.0` are different answers.
- No numeric thresholds, tolerances, timeouts, result limits or sampling are used
  anywhere in RQ1.

### 2.8 Things a reviewer should know

- **The review fingerprint ignores version stamps.** `evidence()` blanks
  `owl:versionInfo` and `owl:versionIRI` before hashing, so a release bump does
  not re-open the 94 recorded review decisions. Every other byte still counts.
  Without this, bumping a version number would look like new evidence.
- **The construct inventory is self-authored.** It maps 104 constructs its own
  maintainers listed. It cannot reveal an omission nobody listed, and the summary
  says so.
- **Byte-level source rules are a separate axis** with no vocabulary term behind
  them, reported separately so they cannot inflate the representation result.

---

## 3. Results, and how to read them

### 3.1 Specification-derived assessment

94 requirements · 210 cases · **0 human reviews pending**

Demonstrated requirements, out of those applicable to each version:

| VCF | Applicable | Expanded | Condensed (structure) | Untested |
| --- | ---: | ---: | ---: | ---: |
| 4.1 | 69 | 32 (46.4%) | 26 (37.7%) | 37 |
| 4.2 | 72 | 34 (47.2%) | 28 (38.9%) | 38 |
| 4.3 | 74 | 35 (47.3%) | 29 (39.2%) | 39 |
| 4.4 | 83 | 38 (45.8%) | 31 (37.3%) | 45 |
| 4.5 | 91 | 51 (56.0%) | 37 (40.7%) | 40 |

**How to read this.** Roughly half of each version's requirements are
demonstrated. The other half are almost entirely **untested, not failed** — the
`not-demonstrated` count is 0 for every version on the expanded profile. So the
honest reading is *"this much is proven, the rest is unmeasured"*, not *"this
much works and the rest is broken"*.

The condensed column is lower on the structure axis by design: that profile
stores sample values as vectors, so a query that walks per-sample resources finds
nothing. That is a storage trade-off, not a loss of information.

### 3.2 What the number is not

- **Not a conformance claim.** The assessment's own label: *"Coverage of
  registered information requirements; specification completeness not
  established."*
- **Not comparable to the 104/104 inventory below.** Different denominators
  counting different things. Never combine them.

### 3.3 Curated construct inventory

**104/104** VCF 4.5 constructs have a preserved, structured representation;
**87** additionally have an enforcement rule. Separately, **333/333** reserved
Number/Type rows extracted from the specification texts match the versioned
registries, and **17/17** fixtures satisfy the byte-level source rules.

**How to read this.** 104/104 means every construct *on the maintainers' list* is
represented. It is a completeness map, not an independent audit, and the gap
between 104/104 and the ~50% above is exactly the difference between "we listed
what we support and we support it" and "we read the specification and tested
against it".

### 3.4 One number that needs care

`queryExecutions` reports **840**. That is the nominal count: 210 cases × 2 axes
× 2 profiles. But 165 of the 210 cases run the *identical* query and expected
answer on both axes, so **375 of those 840 are repeats and only 465 are
distinct** (see `RQ2/analysis/evidence-map.py`). Quote 465, or quote 210 cases
and drop the execution count.

---

## Open issues

1. **The text says "three questions" and lists four** (`long-paper/methods.tex`).
2. **`queryExecutions: 840` is reported without the repeat caveat** in the
   assessment's own summary, which invites the overstatement described in §3.4.
3. **Query construction is not a reproducible procedure** (§2.4, step 2).
   Documented as a pipeline, not as a method; `queries/` has no README and a
   third of requirements carry only boilerplate interpretation.
4. **RQ1 cannot rule out a shared misreading** between the materializer, the
   queries and the vocabulary — see the box in §2.4, step 1. The evidence that
   it is not happening is indirect (81 emitted terms no query consults) and the
   direct check lives in RQ2, not here. Any claim built on RQ1 alone should be
   read with that in mind.
