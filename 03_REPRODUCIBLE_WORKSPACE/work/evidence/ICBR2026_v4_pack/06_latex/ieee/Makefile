# IEEEtran build.  `make`  ->  paper_v4_ieee.pdf
# Override on the command line, e.g.  make MD=/path/to/other.md
SHELL    := /bin/bash
export PATH := /Library/TeX/texbin:/opt/homebrew/bin:$(PATH)
export TEXINPUTS := ../common:$(TEXINPUTS):
PACK     ?= ../..
MD       ?= $(PACK)/02_paper/paper_v4.md
BIB      ?= $(PACK)/05_data_and_code/references.bib
OUT      ?= paper_v4_ieee.pdf
COMMON   := ../common
BUILD    := build
FIGS     := $(wildcard $(PACK)/03_figures/*.png $(PACK)/03_figures/*.pdf $(PACK)/03_figures/*/*.png $(PACK)/03_figures/*/*.pdf)

.PHONY: all clean convert check
all: $(OUT)

# Always re-run the (fast) conversion; latexmk decides what really needs rebuilding.
convert:
	@mkdir -p $(BUILD)
	python3 $(COMMON)/md2tex.py --md $(MD) --outdir $(BUILD) --workdir . \
	    --lua $(COMMON)/filter.lua --bib-real $(BIB)

$(OUT): convert main.tex $(COMMON)/mdcommon.sty $(FIGS)
	latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=$(BUILD) main.tex
	cp $(BUILD)/main.pdf $(OUT)
	@$(MAKE) --no-print-directory check

check:
	@! grep -n -E "Overfull|undefined|Citation .* undefined|Missing character|\[\?\]" $(BUILD)/main.log \
	  || echo "^^^ LaTeX warnings above need attention"
	@echo "built $(OUT)"

clean:
	rm -rf $(BUILD) $(OUT)
