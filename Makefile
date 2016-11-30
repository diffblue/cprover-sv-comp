CBMC=../cbmc

all: 
	mkdir -p tmp
	cp $(CBMC)/LICENSE cbmc tmp/
	cp $(CBMC)/src/cbmc/cbmc tmp/cbmc-binary
	cd tmp; tar cfz ../CBMC-sv-comp-2017.tar.gz *; rm cbmc cbmc-binary LICENSE; cd ..; rm -R tmp
