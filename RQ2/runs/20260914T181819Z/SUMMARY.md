# Reproduction run 20260914T181819Z

Produced by `sh RQ2/run.sh` on 2026-09-14T18:18:23+00:00, 10 steps, 302s total, 0 failures.

| Pinned | |
| --- | --- |
| Vocabulary | `v2.1.2` = `3f06d18` |
| Converter | `v3.0.3` = `be658a2`, image `ecrum19/vcf-rdfizer@sha256:31f1361b6d66591a43e706caeba7c079f498a6ae69d9d279effa82d26beaf57a` |
| Host | Ubuntu 24.04.4 LTS, x86_64, 8 CPU |
| Engines | rdflib 7.6.0 (SPARQL), pyshacl 0.40.1, Docker 29.7.2 |

## Cross-producer replay

The vocabulary's own materializer and the converter were run over the same 10 fixtures in both sample profiles, and every applicable case replayed against the reviewed expected answers.

| Outcome | Checks |
| --- | ---: |
| Both pass | 508 |
| Repo passes, converter fails | 36 |
| Both fail | 28 |
| Converter passes, repo fails | 0 |
| **Total** | **572** |

Requirements exercised: **39**; agreeing on every check: **34**; passing on every check for both producers: **28**.

**5 requirements diverge**, on 36 checks:

| Requirement | Outcomes |
| --- | --- |
| R11 | {'pass/fail': 20} |
| R21 | {'pass/pass': 10, 'pass/fail': 5, 'fail/fail': 5} |
| R27 | {'pass/pass': 5, 'fail/fail': 2, 'pass/fail': 1} |
| R61 | {'pass/pass': 4, 'pass/fail': 4} |
| R89 | {'pass/fail': 6, 'fail/fail': 2} |

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

