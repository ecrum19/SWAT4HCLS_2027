# Worked-example fixtures

The authored fixtures behind the short paper's worked example. They are provenance
for what the manuscript prints, not a runnable experiment — the reproducible
experiments live in [`../RQ1/`](../RQ1/), [`../RQ2/`](../RQ2/), [`../RQ3/`](../RQ3/)
and [`../RQ4/`](../RQ4/).

| File | What it is |
| --- | --- |
| [synthetic.vcf](synthetic.vcf) | One VCF record, two samples. Also the input to RQ2's profile-size figures. |
| [expanded.ttl](expanded.ttl) | That record in the *expanded* profile. |
| [condensed.ttl](condensed.ttl) | The same record in the *condensed* profile. |
| [sample-depth.rq](sample-depth.rq) | The query printed as Listing 1 of the short paper. Expected row: SAMPLE1, 42. |
| [generated/verification.json](generated/verification.json) | The recorded result of checking the two renderings against the source. |

The record is one site with `DP` values of 42 and 7, chosen so a depth threshold
selects exactly one sample. The two renderings hold the same information: the
condensed vectors carry the same values the expanded resources do, but reaching an
individual cell requires decoding rather than a graph pattern.
