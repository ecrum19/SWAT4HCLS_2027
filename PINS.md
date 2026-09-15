# Pinned artifacts

Everything the experiments evaluate, and the digest that fixes it. A tag can be
moved; a digest cannot, so where both exist the digest is what the results
actually depend on.

Each script re-derives these at run time and records them in its own output
(`RQ*/results/run.json`, `RQ2/runs/<stamp>/env.json`), so this page is a
convenience, not the source of truth. If the two disagree, the run record is
right and this page is stale.

## Software under evaluation

| | Version | Commit | Used by |
| --- | --- | --- | --- |
| [vcf-core-vocabulary](https://github.com/ecrum19/vcf-core-vocabulary) | `v2.1.2` | `3f06d188fe1ae72d0841bee45307a392cb3744d4` | RQ1, RQ2, RQ3 |
| [VCF-RDFizer](https://github.com/ecrum19/VCF-RDFizer) | `v3.0.3` | `be658a288b70b7a236dc45d40978b295f8c216b6` | RQ2, RQ3 |

Both are cloned once into `.artifacts/<name>-<tag>/` and shared by all three
scripts. The tag is part of the directory name, so changing a pin fetches a
fresh checkout rather than reusing the previous one.

## Container image

The converter is a host-side wrapper that drives a container, so reproducing a
conversion needs both the wrapper revision above **and** this image.

| Image | Digest |
| --- | --- |
| `ecrum19/vcf-rdfizer` | `sha256:31f1361b6d66591a43e706caeba7c079f498a6ae69d9d279effa82d26beaf57a` |

Pinned by digest, never by tag: `v3.0.3`, `3.0.3` and `latest` all pointed here
when the results were produced, but only the digest is guaranteed to keep doing
so. **The toolchain inside the image is not independently pinned** — RMLStreamer,
QLever, hdtc, bcftools and the rest are fixed only by this digest.

## Specification sources

The VCF texts the requirements are read from, retrieved 2026-09-08 from
`samtools/hts-specs`. The lock file's own note applies: *"URLs can move; hashes
are authoritative."*

| Source | SHA-256 |
| --- | --- |
| VCF 4.1 | `7d29ef8f93745f246202da3e32107ea13b036bbefcb31f7971a3ce31f1045baa` |
| VCF 4.2 | `66dbd167e8fb309708e0956ffbb12808bd338a703fbf034d80d1ead56ae480cc` |
| VCF 4.3 | `332d8b910ac9952bfba04374118f8c4f318ea996d5017599e68f80379fd61cde` |
| VCF 4.4 | `4c88884cf6b016efcec691d5186432a2e0b679396204d14770e89839ef536e1a` |
| VCF 4.5 | `37f13e0d2e8e741ea8505b0342b6e6034637a1f476eeb3af1b8acc25d70246c5` |

Regenerate with `RQ1/methodology/sources.lock.json`.

## Models compared in RQ4

Not evaluated, only read. Digests record what was inspected, so a reader can
tell whether an artifact has changed since. Re-fetch with `sh RQ4/fetch.sh`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| GFVO `gfvo.xml` | 154,699 | `62924be2797db1e90a648d1423abb1a83a22f2f0bceab7fb0835e3686091af97` |
| HERO-Genomics `hero_genomics.ttl` | 478,157 | `6c03ce2d3554fff0bb092b37f4f01249436925fcf0677569821a8ec0af791c47` |
| GVO (content-negotiated Turtle) | 11,815 | `651d1a3431b1282485e061f0c6e62d552876a426a847909991691b551acef53d` |
| VCF2RDF term listing | 41,433 | `9fc2fdc5c87974e93e903937c22c9aa21641300d789b09153de9daea4e06cbb7` |

These four are the least stable things on this page: they are third-party pages
fetched live, with no release tags to hold them still. GVO is served over plain
HTTP only, and HERO's ontology has already moved once.

## What is not pinned

- **The machine.** Recorded per run, not fixed. The Python, rdflib, pySHACL and
  Docker versions differ between the VM and a laptop, and each run says which it
  used.
- **The image's internal toolchain**, as above.
- **Nothing is version-pinned by tag alone** anywhere in the pipeline.
