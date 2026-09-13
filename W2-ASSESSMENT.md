# W2 — Assessment evidence

Completed 2026-09-13 against vcfcv `v2.1.1` (`dd139f9`) and VCF-RDFizer `v3.0.2` (`b8da2ed`)
plus the fixes this workstream prompted (branch `fix/vcf45-structured-accessors`, PR #12, not yet
released). The final figures were produced on the `vcf-bench-2` VM. Scripts and results: [`w2/`](w2/).

## What this adds to the existing assessment

The existing assessment is sound and is not re-derived here. It scores 94 specification-derived
requirements over 210 cases, every expected answer authored before the query ran, every passing
query re-run against an emptied graph. W2 changes one thing: **who produced the RDF.**

`assess.py` builds its witnesses with `from vcf_examples import materialize` — the vocabulary
repository's own 408-line materializer. VCF-RDFizer is a separate program. Both target VCF Core;
the paper cites the first for coverage and the second for implementation. Nothing had checked
that a query and expected answer written against one also holds over the other.

So W2 replays the existing queries and the existing reviewed expected answers over
converter-produced graphs. No expected answer was re-derived: the oracle is
`coverage/methodology/inputs/cases.json` as reviewed and accepted on 11 September.

## W2.1–W2.3 Evidence levels, applied

| Level | What the existing assessment establishes | What W2 adds |
| --- | --- | --- |
| Mechanism exists | 467 declared terms; 104/104 inventoried constructs | unchanged |
| Example instantiates it | 41 fixtures, 210 cases, 840 executions over `vcf_examples` output | the same cases over converter output |
| Behaviour independently checked | queries answer independently authored expectations | **whether that holds for the shipped converter** |

## W2.4–W2.6 The cross-producer check

Ten fixtures — `basic-v4.1` … `basic-v4.5`, `header-audit-v4.5`, `features-v4.5`,
`local-alleles-v4.5`, `tandem-repeats-v4.4/4.5` — covering 143 of the 210 cases and the
difficult decisions W0.3 prioritised. Each converted in both sample profiles (20 conversions, no
failures), then every applicable case replayed against both producers.

```sh
sh w2/convert-fixtures.sh <outdir>          # 20 conversions
python3 w2/cross-producer.py <outdir>       # 572 checks
```

| Outcome | Before the fixes | **After** |
| --- | ---: | ---: |
| Both producers pass | 366 | **508** |
| Repo passes, converter fails | 178 | **36** |
| Both fail | 28 | 28 |
| Converter passes, repo fails | 0 | 0 |

The 28 both-fail checks are all condensed-profile structure queries — the deliberate storage
trade-off the assessment already documents. The producers agree there, before and after.

**42 of 47 requirements now hold for both producers; 5 do not.** The first run of this check
found 15 divergent requirements; nine of them were converter defects or gaps that the check
identified precisely enough to fix, and they were fixed (see below). What remains is a much
smaller and better-understood set.

### What the first run found, and what was fixed

The first run divided the 178 divergent checks into three causes. Acting on them closed nine
requirements — R09, R12, R13, R14, R17, R20, R28, R51 and R83:

- **One correctness defect.** `Number=LA`/`LR` items were bound to global allele indices
  positionally, ignoring the sample's LAA subset, so with `LAA=2,4` the depths `20,30,10` were
  attached to alleles 0, 1, 2 instead of 0, 2, 4 — wrong values, not missing ones. Fixed; R83
  now returns all 18 expected rows, and an item with no LAA to resolve against gets no
  `vcfc:forAllele` rather than a guess.
- **Missing structured accessors.** ID components, FILTER codes with their declaration links,
  `fieldIndex`, record-level `FormatKey` resources and `phaseIndicator` are now emitted. The
  converter also emits `vcfc:MixedPhasing`, which it never did, and the non-deprecated
  `LocalAlleleMembership` form in place of `vcfc:localAlleleIndex`.
- **Base-modification keys were unrecognised.** VCF 4.5 reserves two spellings — `M[0-9]+[ACGTUN]`
  and named aliases such as `M5mC` for `M27551C` — and only the numeric one was accepted, so no
  `BaseModification` resource was ever built. The 30 aliases now resolve, and
  `features-v4.5` emits three `BaseModification` resources where it emitted none.

### The five that remain

36 checks, on five requirements. None is a correctness defect, and none is a limit of the
vocabulary.

| Requirement | Checks | Profile | What it is |
| --- | ---: | --- | --- |
| **R11** QUAL datatype | 20 | both | The materializer writes `"60"^^vcfc:VCFFloat`, the converter `"60"^^xsd:decimal`. `vcfc:QualityShape` accepts six datatypes deliberately, so both conform; only a query projecting `DATATYPE()` can tell them apart. Addressed in the vocabulary rather than either producer — see below. |
| **R89** repeat components | 6 | both | Tandem-repeat fields decompose partially: the summary row appears, the per-allele components are null. |
| **R21** sample fields | 5 | condensed | Needs `vcfc:sampleDataRaw`, which the converter does not emit, to decode a condensed vector. |
| **R61** named Number codes | 4 | both | Value items are not materialised for the named Number codes this requirement exercises. |
| **R27** local alleles | 1 | condensed | A near-miss: the expected empty local-allele list is `""`, the converter encodes it as `"."`. A vector-encoding convention, not a structural gap. |

**R11 was addressed in the vocabulary.** The permissiveness is deliberate — `xsd:double` carries
INF and NaN but not the `INFINITY` spelling VCF allows — so narrowing the range would invalidate
conforming data. `vcfc:qual` now carries explicit guidance instead: producers SHOULD write
`vcfc:VCFFloat`, the shape accepts the numeric alternatives, two conforming graphs of the same
file can differ here, and consumers MUST NOT branch on `DATATYPE(?qual)`. This changes the
released ontology and wants a **2.1.2 bump** before the manuscript cites it.

**R29 was closed by implementing the specification's own counting rule** rather than
approximating it. A `Number=M` field carries one value per base, on either strand, of the
concatenated genotype allele sequences that could hold the modification, in occurrence order;
missing and symbolic alleles contribute none, and `N` yields both strands with the negative
immediately after the positive. The rule reproduces the specification's worked example — an
allele of `CGA` gives two `M5mC` values, the forward-strand C at the first base and the
reverse-strand C at the second.

Each item now carries `vcfc:modifiedBaseOffset`, `vcfc:forAllele` and `vcfc:forBaseModification`.
`vcfc:BaseModification` is keyed by the modification rather than by the FORMAT key that reported
it, so `M5mC`, `DPM5mC` and `ADM5mC` converge on one resource — which is what the R29 queries
ask for, a single `?m` carrying both a fraction and its depth.

Where the payload length and the positions the sequences imply disagree, no item is emitted and
the run counts a mismatch. Binding a value to the wrong base is the failure mode R83 was, and a
whole list on `vcfc:fieldValue` is better than a confidently wrong decomposition.

## W2.7 Semantic round-trip

`w2/round-trip.py` recovers CHROM, POS, ID, REF, ALT, QUAL, FILTER and the GT subfield from
converter RDF and compares them with the source VCF. Recovery is structural by construction:
REF and ALT are rebuilt from the ordered `alleleIndex`/`alleleValue` resources, and GT from
ordered `GenotypeAlleleCall` resources (`callIndex`, `calledAllele`, `isNoCall`) plus
`phasingStatus`. Nothing reads `sampleDataRaw` or any untouched source string — the converter
does not emit one anyway.

**35/35 records recovered across all ten fixtures.**

Two stated limits. INFO and the non-GT FORMAT subfields are out of scope, so this is not
whole-file reconstruction. And `local-alleles-v4.5` writes each site twice, once in local and
once in global form; the check matches on POS and so cannot distinguish the pair — it confirms
one recovery per site, not both.

## W2.8 Denominators

| Number | Counts | Inclusion rule | Supports |
| --- | --- | --- | --- |
| 94 requirements / 210 cases | information requirements read from the VCF 4.1–4.5 specification text | derived section by section from the pinned sources | demonstrated coverage; untested requirements count against it |
| 45.8–56.0 % per version | share of that version's requirements with a passing expanded-profile test | untested scores zero | conservative coverage, not capability |
| 104/104 constructs | a maintainer's inventory of the VCF 4.5 logical model | authored list | per-construct map; cannot reveal an omission nobody listed |
| 333/333 rows | reserved Number/Type rows extracted from the specs | all extracted rows | registry agreement |
| 572 checks / 15 requirements (W2) | cases replayed over both producers | the 10-fixture subset only | cross-producer agreement |

These five denominators count different things and must never be combined.

**Correction owed to the manuscript.** §4.2 and `tab:evidence` still report "491 reviewed
requirements, of which 133 have the required supporting evidence". The current generation has
94 requirements scored per version and per profile; there is no single 133-equivalent figure.
That row must be rewritten from the per-version table, not patched — W5.3.

## W2.9 Gap classification

| Kind | Instances | Threatens the central claim? |
| --- | --- | --- |
| Representation gap (vocabulary cannot express it) | **0** | — |
| Correctness defect | 1 (R83 local alleles) — **fixed** | No longer |
| Missing implementation (structured accessor not built) | 10 requirements — **fixed**; 3 remain (R21, R61, R89) | No — bounds the implementation claim |
| Unresolved interpretation (vocabulary permits both) | 1 (R11 QUAL datatype) — **guidance added** | No |
| Encoding convention | 1 (R27 condensed empty list) | No |
| Deliberate profile trade-off | 28 condensed structure checks | No — already documented |
| Missing evidence (no test yet) | 40 of 91 VCF 4.5 requirements | No — bounds coverage, already stated |

## W2.10 What this means for the paper

The honest summary is neither of the two numbers the paper currently quotes.

The vocabulary is not the limiting factor anywhere: zero divergences trace to something VCF Core
cannot express, and the round-trip recovers every record's fixed columns and genotypes through
structured properties alone. What the cross-producer check establishes is narrower and more
useful than "104/104": **for 42 of 47 requirements exercised in this subset, the coverage the
paper claims is reproducible with the converter the paper cites.** Of the five that are not,
three are accessors the converter has not built, one is a datatype the vocabulary deliberately
leaves open, and one is a condensed-vector encoding convention.

The check also earned its keep as a check. It found a silent correctness defect in VCF 4.5 local
alleles — the manuscript's own headline feature — that no existing test caught, because the
existing tests ran against a different producer. That is the argument for keeping mechanism,
implementation and correctness apart rather than reporting one coverage percentage: the first two
looked fine while the third was wrong.
