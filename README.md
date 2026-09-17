# SWAT4HCLS 2027 manuscript — VCF Core

Two versions of one manuscript, plus the evidence behind them.

| File | Version | Main matter | Total | Limit |
| --- | --- | --- | --- | --- |
| [main_short.tex](main_short.tex) | Five-page ongoing-work paper | 5 | 7 | 5 |
| [long-paper/main_long.tex](long-paper/main_long.tex) | Full paper | **19** | 24 | **12** |

## Build

```sh
make          # both PDFs
make short    # main_short.pdf only
make long     # long-paper/main_long.pdf only
make pages    # last page of main matter, references excluded
make clean    # remove .build/, keep the PDFs
```

Each version compiles in its own `.build/<name>/`, so the two cannot collide.
Requires `latexmk`, `pdflatex` and BibTeX with the packages CEURART uses, including
the `elsarticle-num-names` style; the current PDFs were built with TeX Live 2026.
Both versions share [sources.bib](sources.bib) and the unmodified class in
[template/](template/). There are no external figures — diagrams are TikZ and code
samples are `listings` — so these sources plus a TeX installation are the whole build.

## Evidence

One directory per research question. Each is self-contained and fetches what it
evaluates from GitHub at a pinned revision, so none needs a local checkout of the
vocabulary or the converter. Every directory has an `EXPERIMENT.md` explaining its
premise, procedure, results and known weaknesses; start there.

| | Question | Run |
| --- | --- | --- |
| [RQ1/](RQ1/) | Does VCF Core preserve the intended meaning of the constructs it supports? | `sh RQ1/run.sh` |
| [RQ2/](RQ2/) | Do the version-specific artifacts and the two sample profiles behave as documented? | `sh RQ2/run.sh` |
| [RQ3/](RQ3/) | Does the representation support a reproducible integration task while retaining source context? | `sh RQ3/run.sh` |
| [RQ4/](RQ4/) | How does VCF Core relate to other VCF semantic models? | `sh RQ4/fetch.sh` |

RQ4 is a reading exercise rather than an executed test; its script only re-fetches the
inspected artifacts and records their digests.

[PINS.md](PINS.md) lists every pinned artifact, commit and image digest.
RQ2 writes a self-contained run directory holding the environment, every command with
its exit code and duration, the converted graphs and the results; the run the paper
cites is in [RQ2/runs/](RQ2/runs/).

[coverage/](coverage/README.md) holds the fixtures behind the short paper's worked
example.
