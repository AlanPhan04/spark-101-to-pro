# Book build.  Run from inside book/.
#
#   make build      full build: xelatex -> biber -> xelatex x2  (default)
#   make quick      one xelatex pass, for text-only edits
#   make check      report errors / undefined refs from the last build
#   make clean      remove build artifacts, keep main.pdf
#   make distclean  also remove main.pdf
#   make latexmk    let latexmk work out the pass count itself
#
# Font (fontspec, Times New Roman) and the bibliography (biblatex) require
# XeLaTeX or LuaLaTeX plus biber; plain pdflatex/bibtex will not compile this.

NAME     := main
LATEX    := xelatex -interaction=nonstopmode -file-line-error
BIBER    := biber
LOG      := $(NAME).log

SOURCES  := $(NAME).tex $(wildcard chapters/*.tex) $(wildcard appendices/*.tex) \
            $(wildcard sections/*.tex) sections/ref.bib

.DEFAULT_GOAL := build
.PHONY: build quick check clean distclean latexmk help

build: $(NAME).pdf

$(NAME).pdf: $(SOURCES)
	$(LATEX) $(NAME)
	-$(BIBER) $(NAME)
	$(LATEX) $(NAME)
	$(LATEX) $(NAME)
	@$(MAKE) --no-print-directory check

quick:
	$(LATEX) $(NAME)
	@$(MAKE) --no-print-directory check

check:
	@test -f $(LOG) || { echo "no $(LOG); run 'make build' first"; exit 1; }
	@err=$$(grep -cE '^(\./)?[^ ]*:[0-9]+: |^! ' $(LOG) || true); \
	 und=$$(grep -cE 'Citation .* undefined|Reference .* undefined' $(LOG) || true); \
	 printf 'errors: %s   undefined refs/cites: %s   pages: %s\n' \
	   "$$err" "$$und" "$$(pdfinfo $(NAME).pdf 2>/dev/null | awk '/^Pages/{print $$2}')"; \
	 if [ "$$err" != "0" ] || [ "$$und" != "0" ]; then \
	   echo '--- first 20 ---'; \
	   grep -E '^(\./)?[^ ]*:[0-9]+: |^! |Citation .* undefined|Reference .* undefined' $(LOG) | head -20; \
	   exit 1; \
	 fi

clean:
	rm -f $(NAME).bbl $(NAME).bcf $(NAME).blg $(NAME).run.xml $(NAME).fls $(NAME).fdb_latexmk \
	      $(NAME).log $(NAME).lof $(NAME).lot $(NAME).out $(NAME).toc \
	      $(NAME).synctex.gz comment.cut
	find . -name '*.aux' -delete

distclean: clean
	rm -f $(NAME).pdf

latexmk:
	latexmk -pdflatex=xelatex -pdf -interaction=nonstopmode $(NAME)

help:
	@sed -n '3,10p' Makefile | sed 's/^# \?//'
