# SWAT4HCLS 2027 manuscript — VCF Core

Two versions of the same manuscript are maintained side by side:

| File | Version | Main matter | Total |
| --- | --- | --- | --- |
| [main_short.tex](main_short.tex) | Five-page ongoing-work paper | 5 pages | 7 pages |
| [main_long.tex](main_long.tex) | Full paper (limit: 12 pages of main matter) | 10 pages | 12 pages |

Both share [sources.bib](sources.bib) and the unchanged CEURART class in
[template/](template/). Neither uses external figures: the diagrams are TikZ and
the code samples are `listings` environments, so the sources above plus a TeX Live
installation are everything the build needs.

## Build

From this directory:

```sh
make
```

`make` produces both `main_short.pdf` and `main_long.pdf`. To build one version only:

```sh
make short
make long
```

Each version compiles in its own `.build/<name>/` directory, so the auxiliary files
of the two versions cannot collide. The Makefile copies the sources and template
assets into that directory, runs `latexmk`, and exports the PDF here. Class, margins,
fonts and shell-escape settings are not altered.

Requires `latexmk`, `pdflatex` and BibTeX, plus the LaTeX packages used by CEURART,
including the `elsarticle-num-names` bibliography style. All of these ship with a
full TeX Live 2025 or later installation; the current PDFs were built with TeX Live 2026.

Housekeeping targets:

```sh
make clean      # remove .build/, keep the exported PDFs
make distclean  # also remove the PDFs and the review archive
```

## Length

The full-paper target is **at most 12 pages of main matter**, references excluded.
`\label{endofmain}` sits immediately before the bibliography in both versions, so the
last main-matter page is readable from the build directory after a compile:

```sh
make pages
```

## Evidence fixtures

[coverage/](coverage/README.md) holds the authored fixtures behind the paper's worked
example: one synthetic VCF record, its expanded and condensed RDF renderings, the
SPARQL query used in the manuscript, and the recorded verification results.

**These are included for reading, not for running.** The two scripts in that directory
(`verify.mjs`, `check_figures.py`) belong to the wider `vcf-rdfizer-vocabulary`
repository and depend on its npm dependencies and generated reports; they will not
execute from this bundle on their own. The fixtures and the recorded
`generated/verification.json` are self-describing without them.

## Review status

This remains a working draft. Substantive human review of the scientific claims, the
curated coverage verdicts, the alignment judgements and the AI-use declaration remains
editorial work before submission. A successful compile does not establish venue
compliance or publication readiness.

The curated assessment's current claim is 104/104 inventoried logical-model constructs
under its stated rubric. The independent 4.1–4.5 assessment is provisional; neither
establishes complete VCF conformance. The paper's illustration checks one small
synthetic record and must not be described as a general conversion benchmark.
