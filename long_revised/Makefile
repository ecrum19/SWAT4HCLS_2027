SOURCES = main_long.tex intro_rw.tex methods.tex results.tex discussion.tex sources.bib
ASSETS = ceurart.cls cc-by.pdf ceur-ws-logo.pdf
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all pages clean
all: main_long.pdf

main_long.pdf: $(SOURCES) $(ASSETS) Makefile
	mkdir -p .build
	cp $(SOURCES) $(ASSETS) .build/
	cd .build && $(LATEXMK) main_long.tex
	cp .build/main_long.pdf $@

pages: main_long.pdf
	@sed -n 's/.*{endofmain}{{[^}]*}{\([0-9]*\)}.*/Main matter ends on page \1/p' .build/main_long.aux

clean:
	rm -rf .build
