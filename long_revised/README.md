# Shortened long paper

This directory contains a separate shortened manuscript based on the current `long-paper/` version and its length-reduction plan. All edits and build outputs are confined to `long_revised/`.

## Files and build

- `main_long.tex`: master document, abstract, conclusion, acknowledgments, and AI declaration.
- `intro_rw.tex`, `methods.tex`, `results.tex`, `discussion.tex`: shortened sections.
- `sources.bib`, `ceurart.cls`, `cc-by.pdf`, `ceur-ws-logo.pdf`: copied bibliography and template assets, allowing this directory to build independently.
- `companion-notes.md`: relocated audit details, implementation mechanics, secondary counts, and source links; not part of the submission PDF.

From the repository root:

```sh
make -C long_revised
make -C long_revised pages
```

Or run `make` inside this directory. Builds use `latexmk`, pdfLaTeX, and BibTeX, place intermediates in `.build/`, and export `main_long.pdf` here. They do not invoke the root Makefile or rebuild either original paper. The `pages` target reports the page containing the `endofmain` marker, after acknowledgments and the AI declaration and before references.
