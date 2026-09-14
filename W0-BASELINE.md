# W0 — Evidence baseline

Recorded 2026-09-12. Both repositories clean; every artifact below is a pushed commit.

## W0.1 Pinned inputs

| Input | Pin | Note |
| --- | --- | --- |
| Manuscript | `main_long.tex` (this directory) | |
| VCF Core Vocabulary 2.1.2 | tag `v2.1.2` = `3f06d18` (2026-09-14) | cited as `vcfc210`; supersedes 2.1.1 (`dd139f9`), which every result before 14 September used |
| VCF-RDFizer 3.0.3 | tag `v3.0.3` = `be658a2` (2026-09-14) | cited as `vcfrConverter2026`; carries the corrections this work prompted. See [W3-IMPLEMENTATION.md](W3-IMPLEMENTATION.md) |
| VCF specs 4.1–4.5 | `coverage/methodology/sources.lock.json` | sha256 per version, retrieved 2026-09-08 from samtools/hts-specs |

**Tag history.** The misplaced `v3.0.1` tag was deleted upstream. Version-tagged container
images now exist, but the newest is **3.0.2**, which predates the corrections in the 3.0.3
source — reproducing the recorded results requires building the image from 3.0.3.

**Namespace.** VCF-RDFizer 3.0.3 emits `w3id.org/vcf-core/vocab#` and pins **no** vocabulary
version, so the 2.1.2 relationship rests on the behaviour recorded in W3, not on a declaration.

## W0.2 Reusable evidence

| Asset (in `vcf-core-vocabulary`) | Establishes | Regenerate |
| --- | --- | --- |
| `coverage/methodology/` | 94 spec-derived requirements, 210 cases, 840 nominal query executions (**465 distinct** — see W2.1); expected answers authored before running; every pass has a negative probe. Reviewed and accepted 2026-09-11, `pendingReviews: 0` | `npm run methodology:check` |
| `coverage/vcf45-inventory/` | 104/104 curated VCF 4.5 constructs represented, 87 enforced | `npm run coverage:report` |
| `coverage/methodology/fixtures/` (41), `queries/` | Per-version, per-profile witnesses | — |
| `examples/` incl. `profile-comparison/` | Expanded/condensed illustration + 14 queries | `npm run validate:examples` |
| `mappings/` | 123 SSSOM alignments, 65→103 terms; 116 BH25 mappings held separately | `npm run mappings:check` |
| `shacl/`, `ontology/versions/` | Per-version overlays and reserved-key registries; 333/333 rows match | `npm run validate:shacl` |
| Whole suite | 21/21 fixtures, 0 violations | `npm run validate:force` |

## W0.3 Owners and priorities

| Workstream | Owner | Start |
| --- | --- | --- |
| W3 converter evidence | converter agent | **done** — [W3-IMPLEMENTATION.md](W3-IMPLEMENTATION.md) |
| W1 comparison | comparison agent | **done** — [W1-COMPARISON.md](W1-COMPARISON.md) |
| W2 assessment | assessment agent | **done** — [W2-ASSESSMENT.md](W2-ASSESSMENT.md) |
| W4 integration | integration agent | after W3 |

Shared files, one owner each: `coverage/methodology/inputs/*` (paths are hashed by `assess.py` —
moving any of them voids all recorded review acceptances) and `main_long.tex` (Elias).

Priority decisions needing the strongest evidence, chosen so W1 features and W2 competency
questions overlap: expanded/condensed equivalence; allele-dependent `Number` (`A`/`R`/`G`, and
4.5 `LA`/`LR`/`LG`); missingness vs absence; version transitions (phase separation 4.4→4.5,
local alleles, tandem repeats); file- and header-scoped declarations; source provenance.

## W0.4 Frozen baseline

Counts as of `v2.1.1` / `9b6d85e`. Any later change is a delta, not a correction.

| Measure | Value |
| --- | --- |
| Methodology requirements / cases / query executions | 94 / 210 / 840 nominal, 465 distinct |
| Preservation demonstrated, expanded (4.1–4.5) | 46.4, 47.2, 47.3, 45.8, 56.0 % |
| Structure demonstrated, condensed (4.1–4.5) | 37.7, 38.9, 39.2, 37.3, 40.7 % |
| Curated inventory | 104/104 represented, 87 enforced |
| Reserved Number/Type rows | 333/333 |
| Full validation run | 21/21 fixtures, 0 violations |
| Alignments | 123 mappings, 65 subjects, 103 objects |

**Open drift (for W5.3).** `main_long.tex` §4.2 and `tab:evidence` still report "491 reviewed
requirements, of which 133 have the required supporting evidence". The current generation has
94 requirements scored per version and per profile; there is no single 133-equivalent figure.
That row must be rewritten from the per-version table above, not patched. Every other number in
`tab:evidence` (104/104, 87/104, 333/333, 21 fixtures) still matches the pinned artifacts.
