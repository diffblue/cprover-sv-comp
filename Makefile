CBMC=../cbmc
2LS=../2ls
YEAR=2018

all: cbmc 2ls

cbmc: CBMC-sv-comp-$(YEAR).zip

2ls: 2ls-sv-comp-$(YEAR).zip

.PHONY: cbmc 2ls

%-wrapper: %.inc tool-wrapper.inc
	echo "#!/bin/bash" > $@
	cat $*.inc tool-wrapper.inc >> $@
	chmod 755 $@

CBMC-sv-comp-$(YEAR).zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc
	mkdir -p tmp
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper tmp/cbmc
	cp $(CBMC)/LICENSE tmp/
	cp $(CBMC)/src/cbmc/cbmc tmp/cbmc-binary
	cd tmp && chmod a+rX * && zip ../$@ * && rm cbmc cbmc-binary LICENSE
	rmdir tmp

2ls-sv-comp-$(YEAR).zip: 2ls.inc tool-wrapper.inc $(2LS)/LICENSE $(2LS)/src/2ls/2ls
	mkdir -p tmp
	$(MAKE) 2ls-wrapper
	mv 2ls-wrapper tmp/2ls
	cp $(2LS)/LICENSE tmp/
	cp $(2LS)/src/2ls/2ls tmp/2ls-binary
	cd tmp && chmod a+rX * && zip ../$@ * && rm 2ls 2ls-binary LICENSE
	rmdir tmp
