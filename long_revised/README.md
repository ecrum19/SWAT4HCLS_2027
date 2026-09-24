# Full paper

This directory contains the full manuscript, shortened to the twelve-page limit from the earlier long draft. It is self-contained: all sources, template assets, edits and build outputs live in `long_revised/`.

## Files and build

- `main_long.tex`: master document, abstract, conclusion, acknowledgments, and AI declaration.
- `intro_rw.tex`: introduction, research questions, and related work.
- `methods.tex`: vocabulary representation and shared assessment design.
- `examples/`: tab-delimited counterparts of the printed fixtures, plus the three queries behind Listings 2 and 3 and the R21 worked case, in full; see `examples/README.md`. `example.vcf` backs Listing 1, Figure 1, RQ1's worked cases and, with `annotations.ttl`, RQ3's join table; `queries/` holds Listing 2, the R21 query, and Listing 3's source query. Reduced from the existing local-allele fixtures, without changing the experiment inputs.
- `results.tex`: includes `rq1.tex` through `rq4.tex`, each pairing its method with its results.
- `figures/requirement-coverage.pdf`: vector coverage figure used in RQ1, with SVG and PNG counterparts for reuse.
- `scripts/requirement-coverage.py`: generates the coverage figure from `../RQ1/results/summary.json`, checking the profile counts before plotting.
- `scripts/statement-counts.py`: calculates the Section 3 statement counts for both sample profiles by extrapolating from small files materialized with the pinned VCF Core v2.1.3 materializer; needs the clone that `RQ1/run.sh` fetches into `.artifacts/`.
- `discussion.tex`: discussion and future work.
- `sources.bib`, `ceurart.cls`, `cc-by.pdf`, `ceur-ws-logo.pdf`: copied bibliography and template assets, allowing this directory to build independently.

From the repository root:

```sh
make -C long_revised
make -C long_revised pages
```

Or run `make` inside this directory. Builds use `latexmk`, pdfLaTeX, and BibTeX, place intermediates in `.build/`, and export `main_long.pdf` here. There is no repository-level Makefile; `short_paper/` builds separately in the same way. The `pages` target reports the page containing the `endofmain` marker, after acknowledgments and the AI declaration and before references.

The normal paper build uses the supplied figure PDF. To regenerate PDF, SVG, and PNG versions after changing the results or plot, run `make -C long_revised figures` from the repository root, then rebuild the paper. Figure generation requires Python with Matplotlib and the recorded RQ1 results; use `PYTHON=/path/to/python` to select an interpreter.
