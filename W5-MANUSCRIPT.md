# W5 — Manuscript revision

Executed 2026-09-13 against `main_long.tex`, revised against a review pass, then measured and
cut to length on 2026-09-14. **Main matter ends on page 12** — `make pages`, against the
repository's stated limit of 12 pages of main matter. No undefined references or citations.

## What changed, and why each change was needed

| Task | Change | Why |
| --- | --- | --- |
| **W5.1** | Abstract now reports executed results (508/572, 35/35, the integration example, the defect found) instead of artifact counts alone. §5 reorganised under RQ1–RQ3. | The claim being defended is that interpretation context is *preserved*, which is a behavioural claim. An abstract listing declared terms argues a different, weaker thesis. |
| **W5.2** | New `tab:comparison`: 9 retrieval criteria × 5 models, with the two worked contrasts and three stated limits. | Related work previously asserted the advance ("a substantive development") and then conceded no common rubric had been applied. It now shows the rubric. |
| **W5.3** | **`133/491` deleted.** `tab:evidence` rebuilt from the pinned artifacts with per-version rows. Evidence levels (mechanism / instantiation / independent check) stated before any number. **840 → 465** distinct executions. | The 133/491 figures came from a superseded generation and had no current equivalent. 840 counted 375 re-runs of identical checks. |
| **W5.4** | Implementation names exact versions and states that the fixes are not yet in a tagged release; the 172/149 illustration is relabelled hand-authored; new §5.4 carries W4's executed example; the oncology scenario is cut to three sentences. | W3 found the 172/149 counts were the illustration, not converter output — a reader would have taken them as reproducible. |
| **W5.5** | Conclusion names the four remaining gaps as specific requirements with recorded results. | "Remaining conformance work" is unfalsifiable; the reader cannot tell what is missing. |
| **W5.6** | Recompiled; references, counts and cross-references reconciled. | — |

## Numbers corrected during this work

- **`42 of 47 requirements`** in W2-ASSESSMENT.md was wrong — a stale figure from an earlier
  fixture subset. The pinned results give **39 exercised, 34 agreeing, 28 passing outright, 5
  divergent**. Fixed there and never entered the manuscript.
- **840 executions** → **465 distinct** (W2.1 duplicate pass).
- **172/149 triples** relabelled as the hand-authored illustration; the converter emits 225/159.

## Release gates — two of three closed 2026-09-14

1. ~~The evaluation cites an unreleased converter.~~ **Closed.** VCF-RDFizer `v3.0.3` =
   `be658a2` carries the corrections. §5.4's figures were **re-measured from the tag**, not
   relabelled: the tag differs from the commit originally measured (`025fb7d`) in
   `vcf_rdfizer.py`, so the numbers were re-derived rather than assumed. They are identical —
   the emitter change was a docstring.
2. ~~R11 guidance wants vcfcv 2.1.2.~~ **Closed.** `v2.1.2` = `3f06d18`. Declaredness for the
   §5.4 terms is now checked against that tag.
3. **Container image still lags.** Version-tagged images exist (the earlier "only a mutable
   `latest`" note is out of date), but the newest is **3.0.2**, published 12 September, which
   predates the corrections. There is no 3.0.3 image, so reproducing §5.2–§5.4 means building
   from source. §5.4 now says exactly that.

## Review pass — what it caught

A review of the revised text against the evidence records and result JSON found eleven
substantive errors, all introduced or carried by this revision and all now fixed:

| Was | Is | Why it mattered |
| --- | --- | --- |
| "agree for 508 of 572" | agree 536, both pass 508 | the abstract contradicted the body on the headline figure |
| "assessment of 94 requirements is replayed" | the 39 a ten-fixture subset exercises | implied four times the coverage actually replayed |
| "an independent converter" (×4) | "a second, separately implemented producer" | **both repositories are the same author's**; the paper now says so explicitly |
| 225 expanded triples | 227 | pre-fix figure, in a sentence claiming the fixes were applied |
| "35 targeted regression tests" | 101 | stale; measured by running the suite |
| "2024 SWAT4HCLS Biohackathon" | 2025 | contradicts `sources.bib` |
| 35/35 round-trip, unqualified | + expanded-profile only, one recovery per duplicated site | two stated limits were dropped |
| "allele questions agree in both profiles" | record-level allele questions | two of the nine divergent requirements are local-allele ones |
| "two structured accessors" / "three" | three | same three requirements, two counts, 16 lines apart |
| 347 registry entries vs 333 rows | explained from the methodology's scope note | reader does the subtraction and finds no answer |
| R11 vocabulary change undisclosed | disclosed in §5.4 | the cited 2.1.1 tag does not contain it |
| RQ1–RQ3 declared, never answered | answered with 53/94, 17/36, 27/38 | W5.1's actual requirement |

**Trimming applied** (W5.4): the prospective pharmacogenomic SPARQL listing (it queried an
invented namespace and duplicated the executed example), the three discussion vignettes, the
term-by-term walk in §3.2, and the genotype tutorial in §2.1. **15 → 14 pages.**

## Measured on the VM, 2026-09-14

`vcf-bench-2`, image `vcf-rdfizer:local-025fb7d` built from the working branch, input
`coverage/synthetic.vcf`. Replaces every §5.4 figure, all of which predated the accessor fixes.
Reproduce with [`w5/measure.py`](w5/measure.py); results in
[`w5/generated/example-profiles.json`](w5/generated/example-profiles.json).

```sh
python3 w5/measure.py <expanded.nt.gz> <condensed.nt.gz> <vcf-core-vocabulary checkout> v2.1.1
```

| | Expanded | Condensed |
| --- | ---: | ---: |
| Triples | **242** (was 225 pre-fix; W3 projected 227) | **168** (was 159) |
| Distinct VCF Core terms | **93** (was 79) | **80** (was 69) |
| Terms not declared at `v2.1.1` | **0** | **0** |
| SHACL, shared profile + ontology + RDFS | conforms, 0 violations | conforms, 0 violations |
| SHACL, VCF 4.5 profile | conforms, 0 violations | conforms, 0 violations |

Re-run 2026-09-14 from the **`v3.0.3` tag** against the **`v2.1.2`** term set: every figure
above is unchanged, all four SHACL configurations still conform, and the depth query still
returns `SAMPLE1, 42`.

W3's projected 227 was itself too low: it counted only the typed-accessor fix, while the branch
also emits record identifiers, FILTER codes, `fieldIndex`, record-level `FormatKey` resources
and `phaseIndicator`. Declaredness was re-checked against the **`v2.1.1` git tag**, not the
working tree, so the R11 edit cannot flatter it. `coverage/sample-depth.rq` returns its expected
single row (`SAMPLE1, 42`) against the measured expanded graph.

## Cut to length

13 → 12 pages of main matter, by compressing §5.3's prose and folding the three clinical
scenarios in §6.3 into one paragraph. No evidence was removed.

## Not done

Three author TODOs remain in the source: a GeoSPARQL citation (line 223), a repository deep link
(line 330), and "refine this section" on the BioHackathon paragraph (line 337).
Five pre-existing figures could not be traced to any evidence record and were left as written:
the eleven meta-information line types, the 40/40/67/78/122 registry entries, the 48-inline /
75-bridge mapping split, and the 47-terms-lacking-VRS claim.
