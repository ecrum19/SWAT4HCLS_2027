SOURCES = main_long.tex intro_rw.tex methods.tex results.tex rq1.tex rq2.tex rq3.tex rq4.tex discussion.tex sources.bib
ASSETS = ceurart.cls cc-by.pdf ceur-ws-logo.pdf
FIGURES = figures/requirement-coverage.pdf
PYTHON ?= python3
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all figures pages clean
all: main_long.pdf

main_long.pdf: $(SOURCES) $(ASSETS) $(FIGURES) Makefile
	mkdir -p .build/figures
	cp $(SOURCES) $(ASSETS) .build/
	cp $(FIGURES) .build/figures/
	cd .build && $(LATEXMK) main_long.tex
	cp .build/main_long.pdf $@

figures:
	$(PYTHON) scripts/requirement-coverage.py

pages: main_long.pdf
	@sed -n 's/.*{endofmain}{{[^}]*}{\([0-9]*\)}.*/Main matter ends on page \1/p' .build/main_long.aux

clean:
	rm -rf .build
