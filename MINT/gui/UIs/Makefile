default: all

%_ui.py: %.ui
	pyside-uic $^ | ./uic_filter.sh $@

UIFILES=$(wildcard *.ui)
PYFILES=$(UIFILES:%.ui=%_ui.py)

all: $(PYFILES)


test:
	@echo "UI: $(UIFILES)"
	@echo "PY: $(PYFILES)"
