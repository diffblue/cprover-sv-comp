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

.PHONY: cbmc 2ls jbmc test

REGRESSION_TESTS = regression/test_validate_inputs.py \
                   regression/test_parse_property_file.py \
                   regression/test_parse_result.py \
                   regression/test_process_graphml.py

test: $(REGRESSION_TESTS)
	python3 -m unittest $^

cbmc-path.zip: cbmc_wrapper.py tool_wrapper.py $(CBMC)/LICENSE $(CBMC)/$(CMAKE_BUILD_DIR)/bin/cbmc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-cc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	cp cbmc_wrapper.py $(basename $@)/cbmc
	cp tool_wrapper.py $(basename $@)/
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
	cd $(basename $@) && rm cbmc tool_wrapper.py cbmc-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

cbmc.zip: cbmc_wrapper.py tool_wrapper.py $(CBMC)/LICENSE $(CBMC)/$(CMAKE_BUILD_DIR)/bin/cbmc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-cc $(CBMC)/$(CMAKE_BUILD_DIR)/bin/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	cp cbmc_wrapper.py $(basename $@)/cbmc
	cp tool_wrapper.py $(basename $@)/
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
	cd $(basename $@) && rm cbmc tool_wrapper.py cbmc-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

2ls.zip: 2ls_wrapper.py tool_wrapper.py $(2LS)/LICENSE $(2LS)/src/2ls/2ls $(2LS)/lib/cbmc/src/goto-cc/goto-cc $(2LS)/lib/cbmc/src/goto-instrument/goto-instrument sv-comp-readme.sh
	mkdir -p $(basename $@)
	cp 2ls_wrapper.py $(basename $@)/2ls
	cp tool_wrapper.py $(basename $@)/
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
	cd $(basename $@) && rm 2ls tool_wrapper.py 2ls-binary goto-cc goto-instrument LICENSE README
	rmdir $(basename $@)

jbmc.zip: jbmc_wrapper.py tool_wrapper.py $(JBMC)/LICENSE $(JBMC)/$(CMAKE_BUILD_DIR)/bin/jbmc $(JBMC)/jbmc/lib/java-models-library/target/core-models.jar $(JBMC)/jbmc/lib/java-models-library/target/cprover-api.jar sv-comp-readme.sh
	mkdir -p $(basename $@)
	cp jbmc_wrapper.py $(basename $@)/jbmc
	cp tool_wrapper.py $(basename $@)/
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
	cp -L $(SV_BENCHMARKS)/java/common/org/sosy_lab/sv_benchmarks/ObjectFactory.java $(basename $@)/smoketest/common/org/sosy_lab/sv_benchmarks/
	cp -L $(SV_BENCHMARKS)/java/jbmc-regression/if_expr1/Main.java $(basename $@)/smoketest/true1/
	cp -L $(SV_BENCHMARKS)/java/jbmc-regression/assert2/Main.java $(basename $@)/smoketest/false1/
	echo '#!/usr/bin/env bash' > $(basename $@)/smoketest.sh
	echo 'set -eux pipefail' >> $(basename $@)/smoketest.sh
	echo './jbmc --graphml-witness witness.graphml --propertyfile smoketest/valid-assert.prp smoketest/common smoketest/true1 | tee smoketest/true1/result.log; cat smoketest/true1/result.log | grep TRUE; echo $?' >> $(basename $@)/smoketest.sh
	echo './jbmc --graphml-witness witness.graphml --propertyfile smoketest/valid-assert.prp smoketest/common smoketest/false1 | tee smoketest/false1/result.log; cat smoketest/false1/result.log | grep FALSE; echo $?' >> $(basename $@)/smoketest.sh
	chmod a+rx $(basename $@)/*
	zip -r $@ $(basename $@)
	cd $(basename $@) && rm jbmc tool_wrapper.py jbmc-binary core-models.jar cprover-api.jar LICENSE-for-core-models LICENSE-for-JBMC LICENSE-for-java-cprover-api README smoketest.sh && rm -Rf smoketest
	rmdir $(basename $@)

jbmc-smoketest: jbmc.zip
	mkdir -p temp; rm -Rf temp/*
	cd temp; unzip ../jbmc.zip; cd jbmc; ./smoketest.sh
