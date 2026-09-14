# Isolated, reproducible builds for both manuscript versions.
# Each variant compiles in its own .build/<name>/ directory so that the
# auxiliary files of the short and long versions never collide.

PAPERS   = main_short main_long
PDFS     = main_short.pdf long-paper/main_long.pdf
LONG_SOURCES = long-paper/main_long.tex long-paper/intro_rw.tex long-paper/methods.tex \
	long-paper/results.tex long-paper/discussion.tex
TEMPLATE = template/ceurart.cls template/cc-by.pdf template/ceur-ws-logo.pdf
LATEXMK  = latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error
ZIP      = VCF-Core-SWAT4HCLS-2027-review.zip

.PHONY: all short long pages clean distclean zip

all: $(PDFS)

short: main_short.pdf
long: long-paper/main_long.pdf

main_short.pdf: main_short.tex sources.bib $(TEMPLATE) Makefile
	mkdir -p .build/main_short
	cp main_short.tex sources.bib $(TEMPLATE) .build/main_short/
	cd .build/main_short && $(LATEXMK) main_short.tex
	cp .build/main_short/main_short.pdf $@

long-paper/main_long.pdf: $(LONG_SOURCES) sources.bib $(TEMPLATE) Makefile
	mkdir -p .build/main_long
	cp $(LONG_SOURCES) sources.bib $(TEMPLATE) .build/main_long/
	cd .build/main_long && $(LATEXMK) main_long.tex
	cp .build/main_long/main_long.pdf $@

# Last page of main matter, references excluded (12-page limit for the long version).
pages: $(PDFS)
	@for p in $(PAPERS); do \
	  n=$$(sed -n 's/.*{endofmain}{{[^}]*}{\([0-9]*\)}.*/\1/p' .build/$$p/$$p.aux); \
	  echo "$$p: main matter ends on page $${n:-?}"; \
	done

# Remove build intermediates, keep the exported PDFs.
clean:
	rm -rf .build

# Also remove the exported PDFs and the review archive.
distclean: clean
	rm -f $(PDFS) $(ZIP)

# Self-contained archive for review: sources, template, evidence and both PDFs.
zip: $(PDFS)
	rm -f $(ZIP)
	zip -r $(ZIP) main_short.tex main_short.pdf long-paper sources.bib Makefile README.md \
	  template coverage -x '*.DS_Store' '*/generated/.*'
	@echo "Wrote $(ZIP)"
