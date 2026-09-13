# W5 — Manuscript revision

Executed 2026-09-13 against `main_long.tex`. Compiles clean in `ceurart`: **12 → 15 pages**,
no undefined references or citations, 2 overfull boxes (both pre-existing, the keywords line).

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

## Blocking before submission

1. **The evaluation cites an unreleased converter.** Every result in §5.2–§5.4 used VCF-RDFizer
   3.0.2 *plus* the corrections the cross-producer check prompted (PR #12), which has no tag.
   The manuscript says so honestly, but a reader cannot reproduce it until that release exists.
2. **R11 guidance wants vcfcv 2.1.2.** The manuscript cites 2.1.1 throughout.
3. **No versioned container tags**, so §5.3 has to tell readers to cite a digest.

## Not done

Page count grew 12 → 15. W5.4 asked for term-by-term description to be reduced to create space;
§3 was left untouched. That is the obvious trimming target if length becomes a constraint.
