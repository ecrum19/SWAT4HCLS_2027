# Reproduction run 20260915T192432Z

Produced by `sh RQ2/run.sh` on 2026-09-15T19:24:33+00:00, 9 steps, 26s total, 0 failures.

| Pinned | |
| --- | --- |
| Vocabulary | `v2.1.2` = `3f06d18` |
| Converter | `v3.0.3` = `be658a2`, image `ecrum19/vcf-rdfizer@sha256:31f1361b6d66591a43e706caeba7c079f498a6ae69d9d279effa82d26beaf57a` |
| Host | Ubuntu 24.04.4 LTS, x86_64, 8 CPU |
| Engines | rdflib 7.6.0 (SPARQL), pyshacl 0.40.1, Docker 29.7.2 |

## Cross-producer replay

The vocabulary's own materializer and the converter were run over the same 38 fixtures in both sample profiles, and every applicable case replayed against the reviewed expected answers.

| Outcome | Checks |
| --- | ---: |
| Both pass | 693 |
| Repo passes, converter fails | 102 |
| Both fail | 45 |
| Converter passes, repo fails | 0 |
| **Total** | **840** |

Requirements exercised: **53**; agreeing on every check: **38**; passing on every check for both producers: **32**.

**15 requirements diverge**, on 102 checks:

| Requirement | Outcomes |
| --- | --- |
| R11 | {'pass/fail': 20} |
| R21 | {'pass/pass': 10, 'pass/fail': 5, 'fail/fail': 5} |
| R22 | {'pass/fail': 4} |
| R25 | {'pass/fail': 4} |
| R27 | {'pass/pass': 5, 'fail/fail': 2, 'pass/fail': 1} |
| R30 | {'pass/fail': 2, 'pass/pass': 1, 'fail/fail': 1} |
| R32 | {'pass/fail': 4} |
| R60 | {'pass/fail': 10, 'pass/pass': 5, 'fail/fail': 5} |
| R61 | {'pass/pass': 20, 'pass/fail': 20} |
| R79 | {'pass/fail': 6, 'pass/pass': 3, 'fail/fail': 3} |
| R82 | {'pass/fail': 12, 'pass/pass': 6, 'fail/fail': 6} |
| R84 | {'pass/fail': 2, 'pass/pass': 1, 'fail/fail': 1} |
| R85 | {'pass/fail': 2, 'pass/pass': 1, 'fail/fail': 1} |
| R89 | {'pass/fail': 6, 'fail/fail': 2} |
| R92 | {'pass/fail': 4} |

**Sample profiles** return the same outcome on **352 of 420** comparable checks. The 68 disagreements fall on 15 requirements: R18, R19, R20, R21, R27, R28, R29, R30, R60, R79, R82, R83, R84, R85, R89.

## Semantic round-trip

Rebuilt from structured properties alone, expanded profile: **109/109 records** (CHROM, POS, ID, REF, ALT, QUAL, FILTER) and **151/151 sample genotypes**.

_A leading phase indicator is removed from the source genotype before comparison: it is lexical, and only genotypeString -- an untouched source string this check does not read -- records whether it was written out._

Every header line, recovered by source line number and compared on key and value: **431/431 lines**.

Every INFO entry and non-GT FORMAT subfield, rebuilt from ordered value items rather than from a preserved column: **400/401 values**.

- `local-alleles-v4.5` FORMAT/LAA[sample] at position 4: expected ``, got `not recovered`

## Assessment shape

94 requirements, 210 cases. Nominal executions **840**, of which **375** repeat an identical check, leaving **465** distinct. Signatures shared across cases: 0.

| | Requirements | Tested |
| --- | ---: | ---: |
| RQ1 | 94 | 53 |
| RQ2 | 36 | 17 |
| RQ3 | 38 | 27 |

## Section 5.4 profile figures

| Profile | Triples | Distinct VCF Core terms | Undeclared |
| --- | ---: | ---: | ---: |
| expanded | 242 | 93 | 0 |
| condensed | 168 | 80 | 0 |

Declaredness checked against `v2.1.2` (691 declared local names).

