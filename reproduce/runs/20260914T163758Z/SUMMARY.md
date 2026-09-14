# Reproduction run 20260914T163758Z

Produced by `sh reproduce/run.sh` on 2026-09-14T16:38:44+00:00, 15 steps, 616s total, 0 failures.

| Pinned | |
| --- | --- |
| Vocabulary | `v2.1.2` = `3f06d18` |
| Converter | `v3.0.3` = `be658a2`, image `ecrum19/vcf-rdfizer@sha256:31f1361b6d66591a43e706caeba7c079f498a6ae69d9d279effa82d26beaf57a` |
| Converter, pre-correction | `v3.0.2` = `b8da2ed`, image `ecrum19/vcf-rdfizer@sha256:452ad64b9aafad4abfee26f72469c998226c51b18e4d2c110972146a68c86020` |
| Host | Ubuntu 24.04.4 LTS, x86_64, 8 CPU |
| Engines | rdflib 7.6.0 (SPARQL), pyshacl 0.40.1, Docker 29.7.2 |

## Cross-producer replay

| | Pre-correction | Final |
| --- | ---: | ---: |
| Checks | 572 | 572 |
| Both pass | 366 | 508 |
| Divergent (repo passes, converter fails) | 178 | 36 |
| Both fail | 28 | 28 |
| Converter passes, repo fails | 0 | 0 |

**15 requirements diverged before the corrections; 5 still do.** Every one is accounted for below, so no total needs inferring.

| Requirement | Pre-correction | Final | Disposition |
| --- | --- | --- | --- |
| R09 | {'pass/fail': 20} | {'pass/pass': 20} | corrected |
| R11 | {'pass/fail': 20} | {'pass/fail': 20} | still divergent |
| R12 | {'pass/fail': 20} | {'pass/pass': 20} | corrected |
| R13 | {'pass/fail': 20} | {'pass/pass': 20} | corrected |
| R14 | {'pass/fail': 20} | {'pass/pass': 20} | corrected |
| R17 | {'pass/fail': 20} | {'pass/pass': 20} | corrected |
| R20 | {'pass/fail': 10, 'pass/pass': 5, 'fail/fail': 5} | {'pass/pass': 15, 'fail/fail': 5} | corrected |
| R21 | {'pass/pass': 10, 'pass/fail': 5, 'fail/fail': 5} | {'pass/pass': 10, 'pass/fail': 5, 'fail/fail': 5} | still divergent |
| R27 | {'pass/fail': 5, 'pass/pass': 1, 'fail/fail': 2} | {'pass/pass': 5, 'fail/fail': 2, 'pass/fail': 1} | still divergent |
| R28 | {'pass/fail': 2, 'pass/pass': 1, 'fail/fail': 1} | {'pass/pass': 3, 'fail/fail': 1} | corrected |
| R29 | {'pass/fail': 4, 'pass/pass': 2, 'fail/fail': 2} | {'pass/pass': 6, 'fail/fail': 2} | corrected |
| R51 | {'pass/pass': 20, 'pass/fail': 20} | {'pass/pass': 40} | corrected |
| R61 | {'pass/pass': 4, 'pass/fail': 4} | {'pass/pass': 4, 'pass/fail': 4} | still divergent |
| R83 | {'pass/fail': 2, 'pass/pass': 1, 'fail/fail': 1} | {'pass/pass': 3, 'fail/fail': 1} | corrected |
| R89 | {'pass/fail': 6, 'fail/fail': 2} | {'pass/fail': 6, 'fail/fail': 2} | still divergent |

Corrected (10): R09, R12, R13, R14, R17, R20, R28, R29, R51, R83.  
Still divergent (5): R11, R21, R27, R61, R89.  

Requirements exercised: **39**; agreeing on every check: **34**; passing on every check for both producers: **28**.

**Sample profiles** return the same outcome on **252 of 286** comparable checks. The 34 disagreements fall on 9 requirements: R18, R19, R20, R21, R27, R28, R29, R83, R89.

## Semantic round-trip

**35/35 records** recovered from structured properties alone, expanded profile.

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

## Integration example

**PASS** — 2 rows observed against 2 authored in advance, 3 flagged alterations confirmed absent, 0 problems.

| contig:pos | alteration | depth | sample | via |
| --- | --- | ---: | --- | --- |
| chr1:1 | G>C | 30 | `sample` | `LAD` `Number=LR` |
| chr1:2 | A>T | 25 | `sample` | `LAD` `Number=LR` |

