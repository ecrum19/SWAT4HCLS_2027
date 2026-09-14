# Archived results — superseded, cited by nothing

These are the incremental runs made between 12 and 14 September 2026, while the
converter corrections were still being developed. **The paper does not cite any
number in this directory.** Every reported figure now comes from a single run of
`reproduce/run.sh`, recorded under [`../reproduce/runs/`](../reproduce/runs/).

They also include a comparison against the preceding converter release that the
current run does not make: the evaluation now reports one release, VCF-RDFizer
3.0.3, and nothing else. They are kept only so the earlier commits remain
interpretable.

| Archived | Superseded by |
| --- | --- |
| `w2-generated/` | `reproduce/runs/<stamp>/results/` |
| `w2-graphs/` | `reproduce/runs/<stamp>/graphs/` |
| `w4-generated/` | `reproduce/runs/<stamp>/results/w4-results.json` |
| `w5-generated/`, `w5-graphs/` | `reproduce/runs/<stamp>/results/example-profiles.json`, `graphs/example/` |

## Why they were not good enough

Three problems, all fixed by running everything once from pinned artifacts:

- **The runs were not commensurable.** They were made over three days against a
  moving working branch, so figures from different runs could not be safely
  combined — and were. The count of corrected requirements was reported as nine
  when the data said ten.
- **Results were overwritten in place.** One run's output replaced another's
  before the difference was noticed, because every script wrote to the same
  fixed path.
- **Provenance was assembled after the fact** — `MANIFEST.json` and a hand-written
  `manifest-runtime.json`, both removed — instead of being recorded by the run
  that produced the results.

The replacement records the environment, every command, its exit code and its
duration as the run happens, and pins the container images by digest.
