#!/bin/sh

pd -nrt -path \
	.:/usr/lib/pd/extra/iemnet:/usr/lib/pd/extra/osc:~/src/cvs/MINT/pd/iemrtp:~/src/cvs/MINT/MINTmix/WILMA/pd/lib \
	-send "_WILMA_pwd $(pwd)" \
	$@
