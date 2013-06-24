default: all

SUBMODULES=iemlib \
	iemnet iemrtp osc \
	WILMA

.PHONY: default all clean $(SUBMODULES)

all: clean $(SUBMODULES)

clean:
	rm -f *.pd *.pd_linux

iemlib:
iemnet:
	./link_net ../../../../pd/iemnet
iemrtp:
	./link_rtp ../../../../pd/iemrtp
osc:
	./link_osc ../../../../pd/osc
WILMA:
	./link_WILMA ../../../../pd/WILMA

