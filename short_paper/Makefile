# Isolated, reproducible build for the five-page ongoing-work paper.
# Compiles in .build/ so its auxiliary files never collide with long_revised/.
# The CEURART class and logos come from the shared ../template/ directory.

SOURCES  = main_short.tex sources.bib
TEMPLATE = ../template/ceurart.cls ../template/cc-by.pdf ../template/ceur-ws-logo.pdf
LATEXMK  = latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all pages clean

all: main_short.pdf

main_short.pdf: $(SOURCES) $(TEMPLATE) Makefile
	mkdir -p .build
	cp $(SOURCES) $(TEMPLATE) .build/
	cd .build && $(LATEXMK) main_short.tex
	cp .build/main_short.pdf $@

# Last page of main matter, references excluded (5-page limit for this version).
pages: main_short.pdf
	@sed -n 's/.*{endofmain}{{[^}]*}{\([0-9]*\)}.*/Main matter ends on page \1/p' .build/main_short.aux

clean:
	rm -rf .build
