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
described in §2.4. Without them, a query that returns a constant would "pass".

---

## 2. The code, and what to check before trusting it

### 2.1 What runs

`sh RQ1/run.sh` clones the vocabulary from GitHub at tag `v2.1.2`, then runs
three scripts **inside that clone**:

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

### 2.2 What an "axis" is

Every requirement is tested **twice against the same graph**, under two different
standards of evidence. That is what an axis is: not a different question, but a
different rule about what counts as an acceptable way to reach the answer.

| Axis | The question | The query may… |
| --- | --- | --- |
| **preservation** | Is the information still there at all? | do anything, including pulling apart a packed string |
| **structure** | Is it there *as graph structure*? | **not** use `REPLACE`, `SUBSTR`, `STRBEFORE` or `STRAFTER` |

**A worked example.** Requirement R18 asks whether sample identity, field
identity and read depth can be recovered together. In the condensed profile the
two axes use different queries.

Preservation reaches the packed vector and digs the value out with a regular
expression:

```sparql
?vectorvalue vcfc:declaredBy/vcfc:fieldId "DP" ; vcfc:encodedValues ?packedvalue .
BIND(CONCAT("^(?:[^\t]*\t){", STR(?sampleIndex - 1), "}([^\t]*).*$") AS ?pattern)
BIND(REPLACE(?packedvalue, ?pattern, "$1") AS ?value)
```

It **passes** — the depth genuinely is in the graph. Structure has to follow
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

### 2.3 How one case is scored

A **case** is one requirement, at one VCF version, on one fixture. It is scored
once per sample profile (expanded, condensed) and once per axis (preservation,
structure) — so up to four scored results per case:

1. Build a graph from the fixture using the vocabulary's own Python materializer.
2. Run the query that case names for this profile and axis.
3. Compare the rows returned with the rows written in advance.
4. **Pass** only if they match exactly — same rows, same values, same order.

There is no partial credit and no tolerance.

### 2.4 The two controls that stop a test passing for the wrong reason

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

### 2.5 Definitions you need to read the numbers

| Term | Meaning |
| --- | --- |
| **Requirement** | One thing the VCF specification requires, written down as a question. 94 of them across VCF 4.1–4.5. |
| **Case** | One requirement tested at one VCF version against one fixture. 210 of them, each scored per profile and per axis. |
| **Axis** | One of two standards of evidence applied to the same question — see §2.2. |
| **Profile — expanded** | Each sample's value is its own resource. |
| **Profile — condensed** | Sample values are stored as vectors, for cohort-scale data. |
| **demonstrated** | Every case for that requirement/version/profile passed. |
| **partial** | Some passed, some did not. |
| **not-demonstrated** | Cases exist and none passed. |
| **unassessed** | No test has been written yet. **Counts against the score.** |

### 2.6 Scoring rule, stated plainly

`status()` (`assess.py:41`) gives **no fractional credit** and **never drops an
untested requirement from the denominator**. A requirement with no test scores
zero rather than being excluded. This is why the headline percentages look low:
they are a floor, not a ceiling.

### 2.7 Exclusions and thresholds actually in force

- **Structure-axis string-decoding ban** (§2.2). Enforced by raising an error.
- **Version gating.** A case is rejected unless its fixture's `##fileformat`
  line matches the version the case claims (`assess.py:173`).
- **Untested requirements are included** in every denominator. This is the
  opposite of an exclusion and is the single most important scoring decision.
- No numeric thresholds, tolerances or sampling are used anywhere in RQ1.

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
