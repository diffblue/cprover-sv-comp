CBMC=../cbmc
2LS=../2ls
YEAR=2017

all: cbmc 2ls

cbmc: CBMC-sv-comp-$(YEAR).tar.gz

2ls: 2ls-sv-comp-$(YEAR).tar.gz

.PHONY: cbmc 2ls

%-wrapper: %.inc tool-wrapper.inc
	echo "#!/bin/bash" > $@
	cat $*.inc tool-wrapper.inc >> $@
	chmod 755 $@

CBMC-sv-comp-$(YEAR).tar.gz: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc
	mkdir -p tmp
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper tmp/cbmc
	cp $(CBMC)/LICENSE tmp/
	cp $(CBMC)/src/cbmc/cbmc tmp/cbmc-binary
	cd tmp && tar cfz ../$@ * && rm cbmc cbmc-binary LICENSE
	rmdir tmp

2ls-sv-comp-$(YEAR).tar.gz: 2ls.inc tool-wrapper.inc $(2LS)/LICENSE $(2LS)/src/summarizer/2ls
	mkdir -p tmp
	$(MAKE) 2ls-wrapper
	mv 2ls-wrapper tmp/2ls
	cp $(2LS)/LICENSE tmp/
	cp $(2LS)/src/summarizer/2ls tmp/2ls-binary
	cd tmp && tar cfz ../$@ * && rm 2ls 2ls-binary LICENSE
	rmdir tmp
