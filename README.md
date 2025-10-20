# CPROVER SV-COMP Wrappers and Configuration

#### Prerequisites

### CBMC

By default, this should work:
```
git clone https://github.com/diffblue/cbmc
cd cbmc
cmake -S . -Bbuild
cmake --build build -- -j8
cd ..
https://github.com/diffblue/cprover-sv-comp
cd cprover-sv-comp
```

You can use the following variables in `Makefile` to customize:
- `CBMC`: relative location of CBMC clone; by default `../cbmc`
- `CMAKE_BUILD_DIR`: `cmake` build directory; by default `build`

### JBMC

By default, this should work:
```
git clone https://github.com/diffblue/java-cprover-api
git clone https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks
git clone https://github.com/diffblue/cbmc
cd cbmc
cmake -S . -Bbuild
cmake --build build -- -j8
cd ..
https://github.com/diffblue/cprover-sv-comp
cd cprover-sv-comp
```

You can use the following variables in `Makefile` to customize:
- `JBMC`: relative location of CBMC clone; by default `../cbmc`
- `CMAKE_BUILD_DIR`: `cmake` build directory; by default `build`
- `JAVA_CPROVER_API`: relative location of java-cprover-api clone; by default `../java-cprover-api`

### 2LS

By default, this should work:
```
git clone https://github.com/diffblue/2ls
cd 2ls
./build.sh
cd ..
https://github.com/diffblue/cprover-sv-comp
cd cprover-sv-comp
```

You can use the following variables in `Makefile` to customize:
- `2LS`: relative location of 2LS clone; by default `../2ls`

#### Build package

`make`

#### Build wrapper script

If you you want to build the wrapper script only, use

`make` tool`-wrapper`

where tool is `cbmc`, `jbmc` or `2ls`.

#### Benchexec tool script

* CBMC: https://github.com/sosy-lab/benchexec/blob/master/benchexec/tools/cbmc.py
* JBMC: https://github.com/sosy-lab/benchexec/blob/master/benchexec/tools/jbmc.py
* 2LS: https://github.com/sosy-lab/benchexec/blob/master/benchexec/tools/two_ls.py

#### Benchexec benchmark definition

* CBMC: https://github.com/sosy-lab/sv-comp/blob/master/benchmark-defs/cbmc.xml
* JBMC: https://github.com/sosy-lab/sv-comp/blob/master/benchmark-defs/jbmc.xml
* 2LS: https://github.com/sosy-lab/sv-comp/blob/master/benchmark-defs/2ls.xml

#### License

https://github.com/diffblue/cbmc/blob/master/LICENSE

#### Running experiments in SV-COMP style

```
git clone --depth=1 https://github.com/sosy-lab/sv-benchmarks
git clone https://github.com/sosy-lab/benchexec
cd benchexec
tar xzf ../2ls-sv-comp-2017.tar.gz
wget https://raw.githubusercontent.com/sosy-lab/sv-comp/master/benchmark-defs/2ls.xml
sed -i 's/witness.graphml/${logfile_path_abs}${inputfile_name}-witness.graphml/' 2ls.xml
bin/benchexec 2ls.xml --tasks <those categories that you want to run>
wget https://raw.githubusercontent.com/sosy-lab/sv-comp/master/benchmark-defs/cpa-seq-validate-correctness-witnesses.xml
wget https://raw.githubusercontent.com/sosy-lab/sv-comp/master/benchmark-defs/cpa-seq-validate-violation-witnesses.xml
git clone --depth=1 https://github.com/sosy-lab/cpachecker.git
cd cpachecker
ant
cd ..
ln -s cpachecker/scripts/cpa.sh cpa.sh
ln -s cpachecker/config/ config
# manually tweak the requiredfiles and option name=-witness lines in cpa-seq-validate*.xml
bin/benchexec cpa-seq-validate-correctness-witnesses.xml
PYTHONPATH=. python3 contrib/mergeBenchmarkSets.py #needs more parameters
bin/table-generator results/*xml.bz2
```

Replace 2ls by cbmc to use the above with CBMC.

#### Collecting profiling data
```
bin/benchexec cbmc.xml --tasks <those categories that you want to run> -T 120s
gprof --sum ./cbmc-binary *.gmon.out.*
gprof ./cbmc-profiling gmon.sum > sum.profile
rm gmon.out *.gmon.out.*
```
