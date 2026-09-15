# RQ4 — how the assessment works

> **How does VCF Core relate to other existing VCF semantic models?**

---

## 1. Premise, and why it is built this way

RQ1–RQ3 test VCF Core against the VCF specification. None of them says whether
it was worth building — if an existing model already did this, the contribution
would be redundant.

Answering that honestly is harder than it looks, because the obvious approaches
are all bad:

| Tempting approach | Why it is rejected here |
| --- | --- |
| Count classes and properties per model | Rewards verbosity. GVO has more variation classes than VCF Core has terms, and that says nothing about VCF files. |
| Declare a winner | The models have different purposes. A model that does not represent VCF headers is not *failing* if it never set out to. |
| Test each model by converting VCF with it | Requires writing four converters, and the result would measure our skill with someone else's model. |

So RQ4 does something narrower and checkable: **for each of nine questions a
consumer might ask of a VCF graph, can the model's published artifact answer
it, and what is the evidence?**

### Two design choices that keep it fair

**"Outside stated scope" is a first-class verdict, not a failure.** A model
built to type genomic variation is not deficient for lacking header terms. The
four-value scale separates *cannot* from *was never trying to*.

**The criteria are retrieval questions, not quality judgements.** Each is phrased
so an inspection of the artifact settles it — "is there a term that denotes the
file?" — rather than "does it model files well?"

> **Stated bias.** The nine criteria are the interpretation problems VCF Core was
> built to address, so this is **not a neutral ranking**. A matrix chosen by
> GVO's authors would look different and would be equally legitimate. The paper
> says this; it is the most important caveat on the whole section.

---

## 2. The procedure, and what to check before trusting it

### 2.1 This one is read, not run

RQ1–RQ3 execute code. **RQ4 is a person reading four published artifacts.** There
is no script that produces the verdicts, and no automated check that they are
right. That is a real difference in evidential strength and is why this section
is reported separately.

What *can* be automated is whether a reader is looking at the same artifacts:

```sh
sh RQ4/fetch.sh
```

retrieves all four and records a SHA-256 for each in `artifacts/digests.tsv`. It
scores nothing and never fails on a mismatch — a changed digest is information,
not an error.

### 2.2 The four models, and why these four

Each states a *different* purpose for overlapping subject matter, which is what
makes the contrast informative rather than arbitrary.

| Model | Artifact inspected | Evidence strength |
| --- | --- | --- |
| **GFVO** | `gfvo.xml`, BioInterchange/Ontologies `master` | Ontology inspected |
| **HERO-Genomics** | `hero_genomics.ttl` (4102 triples; 112 classes, 86 object properties, 81 datatype properties) | Ontology inspected |
| **GVO** | `genome-variation.org/resource/gvo`, `owl:versionInfo` 2021-11-18 | Ontology inspected |
| **VCF2RDF** | `diegopenhanut/vcf-resources` `gh-pages`, 59 published term pages under `v4_2/` | Term set inspected; **converter behaviour taken from the paper, not observed** |

**GA4GH VRS is deliberately not scored.** It describes computable variation
identity rather than a source file. Scoring it against file-format criteria would
manufacture a contrast its authors never sought.

### 2.3 The nine criteria

| # | Can a consumer… |
| --- | --- |
| F1 | trace a record back to the file it came from? |
| F2 | read a declaration's ID, Number and Type as data, rather than re-parsing a header string? |
| F3 | read which VCF version the file declares? |
| F4 | address ALT allele *n* by index, so a genotype integer resolves to an allele? |
| F5 | separate ploidy, ordered allele calls and phasing? |
| F6 | get the value for (sample, field) without splitting a `:`-joined cell? |
| F7 | associate a `Number=A/R/G` list item with the allele it belongs to? |
| F8 | distinguish an explicit `.` from "not stated"? |
| F9 | tell from the graph which sample encoding was used? |

### 2.4 The four verdicts, defined

| | Meaning |
| --- | --- |
| **E** — explicitly represented | The inspected artifact provides a documented representation meeting the criterion. |
| **C** — representable with additional conventions | Possible, but requires an addition the inspected model does not itself establish. |
| **S** — outside stated scope | Not part of the model's documented purpose. **Not a defect.** |
| **?** — not established | Evidence insufficient to decide. Absence of located evidence is not proof of impossibility. |

### 2.5 Exclusion criteria actually in force

- **VRS excluded** from scoring, for the reason in §2.2.
- **Only published artifacts count.** A capability described in a paper but absent
  from the released artifact is recorded against the artifact, with the
  discrepancy noted.
- **No `?` verdicts remain.** Every cell was settled by inspection.

### 2.6 What a reviewer should be sceptical about

- **No inter-rater check.** The verdicts were assigned by one reader. There is no
  second opinion and no adjudication procedure.
- **VCF2RDF's column is half-inspected.** Its *term set* was read; its *converter
  output* was not. What its graphs actually contain is taken from the paper.
- **The artifacts move.** HERO's ontology was not at the URL first recorded — the
  original note kept the host but not the path, and re-fetching 404'd until the
  path was found again. `fetch.sh` and the digest file exist so this is
  detectable rather than silent.
- **A model could have been misread.** The mitigation is that every verdict names
  the term or absence it rests on, so a disagreeing reader can check the specific
  claim rather than the conclusion.

---

## 3. Results, and how to read them

### 3.1 The matrix

| | VCF Core | GFVO | HERO | GVO | VCF2RDF |
| --- | :-: | :-: | :-: | :-: | :-: |
| F1 file identity | E | E | E | S | C |
| F2 header declarations | E | S | S | S | **E** |
| F3 version | E | S | S | S | C |
| F4 ordered alleles | E | C | C | S | C |
| F5 genotype structure | E | C | C | S | C |
| F6 per-sample FORMAT | E | C | C | S | C |
| F7 allele-dependent values | E | C | C | S | C |
| F8 missingness | E | S | C | C | C |
| F9 profile choice | E | S | S | S | S |

### 3.2 How to read a row, with the three patterns that matter

**HERO and GVO keep INFO as one literal.** Both `hero:vcfInfo` and `gvo:info`
align to `vcfc:infoRaw` — the whole INFO column as a single string. So the
information survives, but every INFO-derived question requires re-parsing that
string *and* supplying the cardinality rule from outside the graph. That is why
F7 is C rather than E for both.

**GFVO made the opposite choice.** It models particular field *meanings* as
first-class concepts — `AlleleCount`, `Coverage`, `MappingQuality`. That answers
those fields well and leaves the declaration mechanism unaddressed, which is why
F2 is S.

**VCF2RDF is the instructive case, and it corrected an earlier verdict.** Reading
the paper alone suggested a term-free isomorphic mapping. The published artifact
shows otherwise: 59 dereferenceable term pages including `Number`, `Type` and
`Description`. **F2 is therefore E, not C** — an earlier draft had this wrong
because it rested on the paper rather than the artifact. But with no allele-index
term, a consumer must still split the value list and count ALT alleles by
re-reading a literal. *Having the declaration is necessary and, alone,
insufficient.*

### 3.3 Why GVO's column is almost all S

The retrieved ontology declares **48 classes, 12 datatype properties and no
object properties**. Forty-seven of the classes are variation types under a bare
`gvo:Variation` root. With no object property anywhere, nothing can attach to an
allele or a sample as a resource.

**That is not a deficiency.** It is an ontology for typing genomic variation,
doing what it set out to do. Scoring it S across file-format criteria records a
difference of purpose, not a shortfall. Its one C is missingness: a
literal-valued property can carry a `.`, but telling that apart from an absent
triple is a convention the ontology does not supply.

### 3.4 The conclusion this supports — and the one it does not

**Supported:** the difference that distinguishes VCF Core is not breadth of
variation modelling. GVO's 47 variation classes exceed anything VCF Core
attempts. It is that VCF Core represents the *interpretation context* a VCF file
carries about itself — the declaration that gives a field its cardinality, the
version that selects which rule applies, the allele ordinal that makes a genotype
integer resolvable, the sample column that scopes a value. In the inspected
artifacts, that context is either kept as text to re-parse, replaced by concepts
for individual fields, or declared for the header and left unbound for the data.

**Not supported:** that any of these models *could not* represent these things.
"Requires additional conventions" is a statement about what an inspected artifact
establishes, never about what a model's community could build.

---

## Open issues

1. **The manuscript says "three questions" and then lists four**
   (`long-paper/methods.tex`). RQ4 is one of them.
2. **Single-reader verdicts with no second opinion** (§2.6). Cheap mitigation: have
   a second reader score the nine criteria blind and record disagreements.
3. **VCF2RDF's converter output has never been inspected** — only its term set.
   The column is half-evidenced and says so, but running the tool on one fixture
   would settle it.
4. **`review/W1-COMPARISON.md` recorded hosts rather than full URLs**, which is why
   HERO could not be re-fetched from the record. `RQ4/artifacts/digests.tsv` now
   carries exact URLs and digests; the older note should point at it.
