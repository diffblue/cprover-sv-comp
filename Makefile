CBMC=../cbmc
CMAKE_BUILD_DIR=build
2LS=../2ls
JBMC=../cbmc
JAVA_CPROVER_API=../java-cprover-api
SV_BENCHMARKS=../sv-benchmarks

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

cbmc-path.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/$(CMAKE_BUILD_DIR)/bin/cbmc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-cc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	sed -i 's/^.\/cbmc-binary --graphml-witness/.\/cbmc-binary --paths fifo --graphml-witness/' $(basename $@)/cbmc
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(CBMC)/LICENSE $(basename $@)/
	cp -L $(CBMC)/$(CMAKE_BUILD_DIR)/bin/cbmc $(basename $@)/cbmc-binary
	strip $(basename $@)/cbmc-binary
	cp -L $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-cc $(basename $@)/
	strip $(basename $@)/goto-cc
	cp -L $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-instrument $(basename $@)/
	strip $(basename $@)/goto-instrument
	chmod a+rX $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm cbmc cbmc-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

cbmc.zip: cbmc.inc tool-wrapper.inc $(CBMC)/LICENSE $(CBMC)/$(CMAKE_BUILD_DIR)/bin/cbmc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-cc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) cbmc-wrapper
	mv cbmc-wrapper $(basename $@)/cbmc
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(CBMC)/LICENSE $(basename $@)/
	cp -L $(CBMC)/$(CMAKE_BUILD_DIR)/bin/cbmc $(basename $@)/cbmc-binary
	strip $(basename $@)/cbmc-binary
	cp -L $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-cc $(basename $@)/
	strip $(basename $@)/goto-cc
	cp -L $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-instrument $(basename $@)/
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

jbmc.zip: jbmc.inc tool-wrapper.inc $(JBMC)/LICENSE $(JBMC)/$(CMAKE_BUILD_DIR)/bin/jbmc $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar $(JBMC)/jbmc/lib/java-models-library/target/cprover-api.jar sv-comp-readme.sh
	mkdir -p $(basename $@)
	$(MAKE) jbmc-wrapper
	mv jbmc-wrapper $(basename $@)/jbmc
	./sv-comp-readme.sh $(basename $@) > $(basename $@)/README
	cp -L $(JBMC)/LICENSE $(basename $@)/LICENSE-for-JBMC
	cp -L $(JAVA_CPROVER_API)/LICENSE $(basename $@)/LICENSE-for-java-cprover-api
	cp -L $(JBMC)/jbmc/lib/java-models-library/OpenJDK\ \ GPLv2\ +\ Classpath\ Exception.txt $(basename $@)/LICENSE-for-core-models
	cp -L $(JBMC)/$(CMAKE_BUILD_DIR)/bin/jbmc $(basename $@)/jbmc-binary
	strip $(basename $@)/jbmc-binary
	cp -L $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar $(basename $@)/
	cp -L $(JBMC)/jbmc/lib/java-models-library/target/cprover-api.jar $(basename $@)/
	mkdir -p $(basename $@)/smoketest/true1
	mkdir -p $(basename $@)/smoketest/false1
	mkdir -p $(basename $@)/smoketest/common/org/sosy_lab/sv_benchmarks
	cp -L $(SV_BENCHMARKS)/java/properties/valid-assert.prp $(basename $@)/smoketest/valid-assert.prp
	cp -L $(SV_BENCHMARKS)/java/common/org/sosy_lab/sv_benchmarks/Verifier.java $(basename $@)/smoketest/common/org/sosy_lab/sv_benchmarks/
	cp -L $(SV_BENCHMARKS)/java/jbmc-regression/if_expr1/Main.java $(basename $@)/smoketest/true1/
	cp -L $(SV_BENCHMARKS)/java/jbmc-regression/assert2/Main.java $(basename $@)/smoketest/false1/
	echo '#!/usr/bin/bash' > $(basename $@)/smoketest.sh
	echo 'set -eux pipefail' > $(basename $@)/smoketest.sh
	echo './jbmc --graphml-witness witness.graphml --propertyfile smoketest/valid-assert.prp smoketest/common smoketest/true1 | tee smoketest/true1/result.log; cat smoketest/true1/result.log | grep TRUE; echo $?' >> $(basename $@)/smoketest.sh
	echo './jbmc --graphml-witness witness.graphml --propertyfile smoketest/valid-assert.prp smoketest/common smoketest/false1 | tee smoketest/false1/result.log; cat smoketest/false1/result.log | grep FALSE; echo $?' >> $(basename $@)/smoketest.sh
	chmod a+rx $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm jbmc jbmc-binary core-models.jar cprover-api.jar LICENSE-for-core-models LICENSE-for-JBMC LICENSE-for-java-cprover-api README smoketest.sh && rm -Rf smoketest
	rmdir $(basename $@)

jbmc-smoketest: jbmc.zip
	mkdir -p temp; rm -Rf temp/*
	cd temp; unzip ../jbmc.zip; cd jbmc; ./smoketest.sh
