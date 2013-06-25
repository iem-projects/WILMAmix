default: all

## the .ui files should be edited with `designer-qt4`

%_ui.py: %.ui
	pyside-uic $^ | ./uic_filter.sh $@

UIFILES=$(wildcard *.ui)
PYFILES=$(UIFILES:%.ui=%_ui.py)

all: $(PYFILES)


test:
	@echo "UI: $(UIFILES)"
	@echo "PY: $(PYFILES)"
