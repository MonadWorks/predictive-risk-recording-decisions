# Springer Nature (sn-jnl) build.  `make`  ->  paper_v4_biomed.pdf
# Override on the command line, e.g.  make MD=/path/to/other.md
SHELL    := /bin/bash
export PATH := /Library/TeX/texbin:/opt/homebrew/bin:$(PATH)
export TEXINPUTS := ../common:sn-template:$(TEXINPUTS):
export BSTINPUTS := sn-template:$(BSTINPUTS):
PACK     ?= ../..
MD       ?= $(PACK)/02_paper/paper_v4.md
BIB      ?= $(PACK)/05_data_and_code/references.bib
OUT      ?= paper_v4_biomed.pdf
COMMON   := ../common
# make LINENO=1 -> line-numbered (review) version; REFSTYLE=sn-nature|sn-vancouver-num|sn-mathphys-num
LINENO   ?= 0
NOTES    ?= 0
REFSTYLE ?= sn-nature
comma    := ,
CLSOPT   := pdflatex,$(REFSTYLE)$(if $(filter 1,$(LINENO)),$(comma)lineno)
BUILD    := build
FIGS     := $(wildcard $(PACK)/03_figures/*.png $(PACK)/03_figures/*.pdf $(PACK)/03_figures/*/*.png $(PACK)/03_figures/*/*.pdf)

.PHONY: all clean convert check
all: $(OUT)

# Always re-run the (fast) conversion; latexmk decides what really needs rebuilding.
convert:
	@mkdir -p $(BUILD)
	@echo '\def\clsopts{$(CLSOPT)}' > $(BUILD)/clsopts.new; cmp -s $(BUILD)/clsopts.new $(BUILD)/clsopts.tex || mv $(BUILD)/clsopts.new $(BUILD)/clsopts.tex
	python3 $(COMMON)/md2tex.py --md $(MD) --outdir $(BUILD) --workdir . \
	    --lua $(COMMON)/filter.lua --bib-real $(BIB)
	@# internal audit remarks live in bib 'note' fields; hide them from the typeset list unless NOTES=1
	$(if $(filter 1,$(NOTES)),,perl -pi -e 's/^(\s*)note(\s*=)/$$1xnote$$2/' $(BUILD)/references.bib)
	@# single column: starred floats -> plain floats, uncaptioned tables / appendix figures pinned
	python3 fix_floats.py

$(OUT): convert main.tex Makefile $(COMMON)/mdcommon.sty $(FIGS)
	latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=$(BUILD) main.tex
	cp $(BUILD)/main.pdf $(OUT)
	@$(MAKE) --no-print-directory check

check:
	@! grep -n -E "Overfull|undefined|Citation .* undefined|Missing character|\[\?\]" $(BUILD)/main.log \
	  || echo "^^^ LaTeX warnings above need attention"
	@echo "built $(OUT)"

clean:
	rm -rf $(BUILD) $(OUT)
