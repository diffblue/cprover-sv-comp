CBMC=../cbmc
2LS=../2ls
JBMC=../cbmc
YEAR=2018

all: cbmc 2ls jbmc

cbmc: cbmc.zip

2ls: 2ls.zip

jbmc: jbmc.zip

.PHONY: cbmc 2ls jbmc

%-wrapper: %.inc tool-wrapper.inc
	echo "#!/bin/bash" > $@
	cat $*.inc tool-wrapper.inc >> $@
	chmod 755 $@

cbmc.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	cp $(CBMC)/LICENSE $(basename $@)/
	cp $(CBMC)/src/cbmc/cbmc $(basename $@)/cbmc-binary
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm cbmc cbmc-binary LICENSE
	rmdir $(basename $@)

2ls.zip: 2ls.inc tool-wrapper.inc $(2LS)/LICENSE $(2LS)/src/2ls/2ls
	mkdir -p $(basename $@)
	$(MAKE) 2ls-wrapper
	mv 2ls-wrapper $(basename $@)/2ls
	cp $(2LS)/LICENSE $(basename $@)/
	cp $(2LS)/src/2ls/2ls $(basename $@)/2ls-binary
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm 2ls 2ls-binary LICENSE
	rmdir $(basename $@)

jbmc.zip: jbmc.inc tool-wrapper.inc $(JBMC)/LICENSE $(JBMC)/src/jbmc/jbmc
	mkdir -p $(basename $@)
	$(MAKE) jbmc-wrapper
	mv jbmc-wrapper $(basename $@)/jbmc
	cp $(JBMC)/LICENSE $(basename $@)/
	cp $(JBMC)/src/jbmc/jbmc $(basename $@)/jbmc-binary
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm jbmc jbmc-binary LICENSE
	rmdir $(basename $@)
