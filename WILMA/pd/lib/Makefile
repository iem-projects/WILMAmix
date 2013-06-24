default: all

SUBMODULES=iemlib \
	iemnet iemrtp osc \
	WILMA

.PHONY: default all clean $(SUBMODULES)

all: clean $(SUBMODULES)

clean:
	find . -type l -delete

iemlib:
iemnet:
	./link_net.sh ../../../../pd/iemnet
iemrtp:
	./link_rtp.sh ../../../../pd/iemrtp
osc:
	./link_osc.sh ../../../../pd/osc
WILMA:
	./link_WILMA.sh ../../../../pd/WILMA

