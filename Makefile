CBMC=../cbmc
2LS=../2ls
JBMC=../cbmc
JAVA_CPROVER_API=../java-cprover-api

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

cbmc-path.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc $(CBMC)/src/goto-cc/goto-cc $(CBMC)/src/goto-instrument/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	sed -i 's/^.\/cbmc-binary --graphml-witness/.\/cbmc-binary --paths fifo --graphml-witness/' $(basename $@)/cbmc
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(CBMC)/LICENSE $(basename $@)/
	cp -L $(CBMC)/src/cbmc/cbmc $(basename $@)/cbmc-binary
	strip $(basename $@)/cbmc-binary
	cp -L $(CBMC)/src/goto-cc/goto-cc $(basename $@)/
	strip $(basename $@)/goto-cc
	cp -L $(CBMC)/src/goto-instrument/goto-instrument $(basename $@)/
	strip $(basename $@)/goto-instrument
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm cbmc cbmc-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

cbmc.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/src/cbmc/cbmc $(CBMC)/src/goto-cc/goto-cc $(CBMC)/src/goto-instrument/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(CBMC)/LICENSE $(basename $@)/
	cp -L $(CBMC)/src/cbmc/cbmc $(basename $@)/cbmc-binary
	strip $(basename $@)/cbmc-binary
	cp -L $(CBMC)/src/goto-cc/goto-cc $(basename $@)/
	strip $(basename $@)/goto-cc
	cp -L $(CBMC)/src/goto-instrument/goto-instrument $(basename $@)/
	strip $(basename $@)/goto-instrument
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm cbmc cbmc-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

2ls.zip: 2ls.inc tool-wrapper.inc $(2LS)/LICENSE $(2LS)/src/2ls/2ls $(2LS)/lib/cbmc/src/goto-cc/goto-cc $(2LS)/lib/cbmc/src/goto-instrument/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) 2ls-wrapper
	mv 2ls-wrapper $(basename $@)/2ls
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(2LS)/LICENSE $(basename $@)/
	cp -L $(2LS)/src/2ls/2ls $(basename $@)/2ls-binary
	strip $(basename $@)/2ls-binary
	cp -L $(2LS)/lib/cbmc/src/goto-cc/goto-cc $(basename $@)/
	strip $(basename $@)/goto-cc
	cp -L $(2LS)/lib/cbmc/src/goto-instrument/goto-instrument $(basename $@)/
	strip $(basename $@)/goto-instrument
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm 2ls 2ls-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

jbmc.zip: jbmc.inc tool-wrapper.inc $(JBMC)/LICENSE $(JBMC)/jbmc/src/jbmc/jbmc $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar $(JBMC)/jbmc/lib/java-models-library/target/cprover-api.jar sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) jbmc-wrapper
	mv jbmc-wrapper $(basename $@)/jbmc
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(JBMC)/LICENSE $(basename $@)/LICENSE-for-JBMC
	cp -L $(JAVA_CPROVER_API)/LICENSE $(basename $@)/LICENSE-for-java-cprover-api
	cp -L $(JBMC)/jbmc/lib/java-models-library/OpenJDK\ \ GPLv2\ +\ Classpath\ Exception.txt $(basename $@)/LICENSE-for-core-models
	cp -L $(JBMC)/jbmc/src/jbmc/jbmc $(basename $@)/jbmc-binary
	strip $(basename $@)/jbmc-binary
	cp -L $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar $(basename $@)/
	cp -L $(JBMC)/jbmc/lib/java-models-library/target/cprover-api.jar $(basename $@)/
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm jbmc jbmc-binary core-models.jar cprover-api.jar LICENSE-for-core-models LICENSE-for-JBMC LICENSE-for-java-cprover-api README
	rmdir $(basename $@)
