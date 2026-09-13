# Plan vs. delivered

Checked 2026-09-13 against [VCF_Core_Long_Paper_Task_Checklist.md](VCF_Core_Long_Paper_Task_Checklist.md);
W1.4, W2.1 and W2.4 completed the same day and re-scored.
**Yes** = done and evidenced · **Partial** = done within a stated bound · **No** = not started.

## W0 — Evidence baseline · complete

| Task | | Evidence |
| --- | :-: | --- |
| W0.1 Pin the inputs | Yes* | [W0-BASELINE.md](W0-BASELINE.md) §W0.1 |
| W0.2 Locate reusable evidence | Yes | §W0.2, 7 assets with regeneration commands |
| W0.3 Assign owners, select priorities | Yes | §W0.3 |
| W0.4 Separate baseline from changes | Yes | §W0.4 frozen counts; W2 reports before/after separately |

\* **Deviation, deliberate:** the plan named vcfcv 2.1.0 and VCF-RDFizer v2.x. The pinned artifacts are
vcfcv **2.1.1** (`dd139f9`) and VCF-RDFizer **3.0.2** (`b8da2ed`) — the releases that existed when W0 ran.

## W1 — Comparison · complete

| Task | | Evidence |
| --- | :-: | --- |
| W1.1 Small comparison set | Yes | [W1-COMPARISON.md](W1-COMPARISON.md) §W1.1 — 4 models, each justified; VRS excluded with reason |
| W1.2 8–12 features | Yes | 9 features F1–F9 |
| W1.3 Operational criteria | Yes | criterion column, one retrieval question each |
| W1.4 Inspect pinned artifacts | Yes | all four artifacts inspected 2026-09-13 — GVO over plain HTTP (`versionInfo` 2021-11-18), VCF2RDF's published term set (`diegopenhanut/vcf-resources`). **No `?` cells remain**; GVO's three resolved to *outside scope*, VCF2RDF's F2 corrected C→**E** |
| W1.5 Populate comparison | Yes | 9×5 matrix, four statuses, evidence paragraph per column |
| W1.6 Worked contrasts | Yes | two: allele-dependent values, version-conditioned interpretation |
| W1.7 Bounded conclusion | Yes | §W1.7, three stated limits, no overall winner; revised after W1.4 completed |

## W2 — Assessment · complete within one bound

| Task | | Evidence |
| --- | :-: | --- |
| W2.1 Inventory test capabilities | Yes | §W2.1 via [`w2/evidence-map.py`](w2/evidence-map.py) — RQ1–RQ3 and F1–F9 mapped, duplicate pass run: **0 cross-case duplicates, 375 of 840 executions redundant**, F7 thinnest at 4/11 |
| W2.2 Distinguish evidence strength | Yes | §W2.1–W2.3 table, with execution status |
| W2.3 Compact evidence map | Yes | by reuse, as instructed — extends `coverage/methodology/` with a producer axis rather than a parallel tracker |
| W2.4 8–12 competency questions | Yes | §W2.4 — **12 named CQs** with executed results and profile agreement; three version transitions; expanded/condensed equivalence stated precisely (252/286). The 572-check replay remains the broader evidence behind them |
| W2.5 Independent expected answers | Yes | `cases.json` as reviewed 2026-09-11; nothing re-derived from converter output |
| W2.6 Execute and report | Yes | `w2/generated/cross-producer.json` — 508 both-pass, 36 divergent, 5 requirements; 9 claim-critical requirements fixed |
| W2.7 Semantic round-trip | **Partial** | 35/35 records, structural recovery only. **Expanded profile only** — condensed decoding is blocked on R21 (converter emits no `vcfc:sampleDataRaw`) |
| W2.8 Explain each denominator | Yes | §W2.8, five denominators, stated as non-combinable |
| W2.9 Classify gaps | Yes | §W2.9 — 0 representation gaps; 1 correctness defect, fixed |
| W2.10 Readable summary | Yes | §W2.10 |

## W3 — Implementation · complete

| Task | | Evidence |
| --- | :-: | --- |
| W3.1 Exact release | Yes | [W3-IMPLEMENTATION.md](W3-IMPLEMENTATION.md) §W3.1, incl. image digest — **no versioned image tags exist** |
| W3.2 Check emitted representation | Yes | 148/148 local names declared in 2.1.1; 0 undeclared terms in either profile |
| W3.3 Reproducible conversion | Yes | §W3.3, both profiles, commands + SHACL matrix |
| W3.4 Support boundary | Yes | §W3.4 states what is *not* established (other 388 terms, VCF 4.1–4.4, larger inputs) |

## W4 — Integration example · complete

| Task | | Evidence |
| --- | :-: | --- |
| W4.1 Bound the example | Yes | [W4-INTEGRATION.md](W4-INTEGRATION.md) §W4.1 — allele-dependent values under 4.5 local alleles |
| W4.2 Document inputs | Yes | §W4.2; annotation snapshot pinned and labelled synthetic in the file |
| W4.3 Explicit links + assumptions | Yes | §W4.3 — join rule in `w4/local-allele-evidence.rq`; sample ≠ patient stated |
| W4.4 Implement the query | Yes | `w4/local-allele-evidence.rq`, returns file/record/sample/declaration |
| W4.5 Expected vs observed | Yes | `w4/expected.json` authored first; PASS, 2 rows, 3 exclusions confirmed by identity |
| W4.6 Reproduction + limitations | Yes | `sh w4/run.sh …`; limitations stated |

**Plan's discrimination requirement met:** the same query over the pre-fix converter returns the same
row count with different alterations — the two `expected.json` predicted, at the predicted depths.

## W5 — Manuscript · not started

W5.1–W5.6: **No.** `main_long.tex` is unchanged by W1–W4; §4.2 and `tab:evidence` still carry the
stale "133/491" figures ([main_long.tex:352](main_long.tex:352), [:368](main_long.tex:368)).

Three numbers W5.3 must carry in: the per-version requirement table in place of 133/491; **465**
rather than 840 wherever an execution count appears; and the profile claim as *equivalent for
file/header/allele questions, divergent by design for per-sample structure queries* rather than
equivalent outright.

## Final completion gate

| Gate | | Note |
| --- | :-: | --- |
| Comparison answers novelty with sourced evidence | Yes | W1 |
| Mechanism / instantiation / checked behaviour distinguishable | Yes | W2.1–W2.3 |
| Version & profile claims executed; denominators understandable | **Partial** | denominators grounded and now audited (840 nominal → **465 distinct**); condensed round-trip still not executed, and the manuscript's denominators are not yet corrected (W5.3) |
| Exact tested release produces the described representation | **Partial** | true for 3.0.2 **plus PR #12**, which is unmerged and unreleased; the published image predates every fix |
| Integration example with checked answers and provenance | Yes | W4 |
| Limitations explicit; no conclusion rests on unexecuted work | Yes | in W0–W4. Not yet true of the manuscript |

## Open before W5 can close the gates

1. **PR #12** merged and released (carries R83, the accessors, R29) — author's call.
2. **vcfcv 2.1.2** bump for the R11 QUAL guidance the manuscript would cite.
3. **Image rebuilt and versioned tags pushed** — reproduction currently needs a digest, not a version.
4. Optional, bounded and documented: condensed round-trip (needs R21).
