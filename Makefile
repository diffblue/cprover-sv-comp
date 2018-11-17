CBMC=../cbmc
2LS=../2ls
JBMC=../cbmc
YEAR=2019

all: cbmc 2ls jbmc

cbmc: cbmc.zip

cbmc-path: cbmc-path.zip

2ls: 2ls.zip

jbmc: jbmc.zip

.PHONY: cbmc 2ls jbmc

%-wrapper: %.inc tool-wrapper.inc
	echo "#!/bin/bash" > $@
	cat $*.inc tool-wrapper.inc >> $@
	chmod 755 $@

cbmc-path.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc $(CBMC)/src/goto-cc/goto-cc
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	sed -i 's/^.\/cbmc-binary --graphml-witness/.\/cbmc-binary --paths fifo --graphml-witness/' $(basename $@)/cbmc
	cp -L $(CBMC)/LICENSE $(basename $@)/
	cp -L $(CBMC)/src/cbmc/cbmc $(basename $@)/cbmc-binary
	cp -L $(CBMC)/src/goto-cc/goto-cc $(basename $@)/
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm cbmc cbmc-binary goto-cc LICENSE
	rmdir $(basename $@)

cbmc.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc $(CBMC)/src/goto-cc/goto-cc
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	cp $(CBMC)/LICENSE $(basename $@)/
	cp $(CBMC)/src/cbmc/cbmc $(basename $@)/cbmc-binary
	cp $(CBMC)/src/goto-cc/goto-cc $(basename $@)/
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm cbmc cbmc-binary goto-cc LICENSE
	rmdir $(basename $@)

2ls.zip: 2ls.inc tool-wrapper.inc $(2LS)/LICENSE $(2LS)/src/2ls/2ls $(2LS)/cbmc/src/goto-cc/goto-cc
	mkdir -p $(basename $@)
	$(MAKE) 2ls-wrapper
	mv 2ls-wrapper $(basename $@)/2ls
	cp $(2LS)/LICENSE $(basename $@)/
	cp $(2LS)/src/2ls/2ls $(basename $@)/2ls-binary
	cp $(2LS)/cbmc/src/goto-cc/goto-cc $(basename $@)/
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm 2ls 2ls-binary goto-cc LICENSE
	rmdir $(basename $@)

jbmc.zip: jbmc.inc tool-wrapper.inc $(JBMC)/LICENSE $(JBMC)/jbmc/src/jbmc/jbmc $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar
	mkdir -p $(basename $@)
	$(MAKE) jbmc-wrapper
	mv jbmc-wrapper $(basename $@)/jbmc
	cp $(JBMC)/LICENSE $(basename $@)/
	cp $(JBMC)/jbmc/src/jbmc/jbmc $(basename $@)/jbmc-binary
	cp $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar $(basename $@)/
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm jbmc jbmc-binary core-models.jar LICENSE
	rmdir $(basename $@)
