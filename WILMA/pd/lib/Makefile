default: all

SUBMODULES=iemlib \
	iemnet iemrtp osc \
	WILMA

.PHONY: default all clean $(SUBMODULES)

all: clean $(SUBMODULES)

clean:
	find . -type l -delete

iemlib:
	./link_iemlib.sh ../../../../pd/iemlib/lib
iemnet:
	./link_net.sh ../../../../pd/iemnet
iemrtp:
	./link_rtp.sh ../../../../pd/iemrtp
osc:
	./link_osc.sh ../../../../pd/osc
WILMA:
	./link_WILMA.sh ../../../../pd/WILMA

