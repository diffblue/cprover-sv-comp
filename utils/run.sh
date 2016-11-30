#!/bin/bash

set -e

export TMPDIR=$PWD
ulimit -S -v 24000000

# test.pl
export PATH=$PWD/../cbmc/regression:$PATH
export TOOL=$PWD/cbmc

cd sv-benchmarks.git/c/cprover-regr/

for category in * ; do
  [ -d $category ] || continue

  echo "Category: $category"

  for d in * ; do
    echo "Subset: $d"
    cd $d
    
    test.pl -j 8 -c "timeout 900 $TOOL"

    #cd ..
    #continue
    cp -a /import/debian-mole/tools-from-svns/cpachecker/CPAchecker.svn/config/ .
    for x in * ; do
      if [ -s $x/main.cex ] ; then
        sed -i "s/main.c/$x\/main.c/" $x/main.cex
        if \
        /import/debian-mole/tools-from-svns/cpachecker/CPAchecker.svn/scripts/cpa.sh -witness-validation \
          -timelimit 90 \
          -spec $x/main.cex \
          -spec ../../../$d/ALL.prp \
          $x/main.[ci] | \
        grep "^Verification result: FALSE" ; then
          echo "$x: Witness confirmed by CPAchecker"
        else
          echo "$x: Witness NOT confirmed by CPAchecker"
        fi
        continue

        ## ec=0
        ## if grep -q -- --32 $x/test.desc ; then
        ##   timeout -k15 90 cbmc --32 --verify-cex $x/main.cex $x/main.[ci] > $x/verify.log || \
        ##     ec=$?
        ## else
        ##   timeout -k15 90 cbmc --verify-cex $x/main.cex $x/main.[ci] > $x/verify.log || \
        ##     ec=$?
        ## fi
        ## if [ $ec -eq 10 ] ; then
        ##   echo "$x: Witness confirmed by CBMC"
        ## else
        ##   echo "$x: Witness NOT confirmed by CBMC"
        ## fi
      fi
    done
   
    cd ..
    ## continue

    ## rm -f tests.log 
    ## echo "Experimental configurations"

    ## for d in * ; do
    ##   sed -i '3s/^/--graphml-cex main.cex /' $d/test.desc
    ## done

    ## echo "CBMC with GraphML counter examples"
    ## mv ../../../bin/cbmc ../../../bin/cbmc-trunk
    ## mv ../../../bin/cbmc-graphml-cex ../../../bin/cbmc
    ## test.pl -j 4 -c "timeout 900 inc.sh"
    ## mv ../../../bin/cbmc ../../../bin/cbmc-graphml-cex
    ## mv ../../../bin/cbmc-trunk ../../../bin/cbmc
   
    ## rm -f tests.log 

    ## for d in * ; do
    ##   sed -i '3s/^--graphml-cex main.cex //' $d/test.desc
    ## done
   
    ## echo "Building goto binaries" 
    ## for d in * ; do
    ##   if grep -q -- --32 $d/test.desc ; then
    ##     goto-cc -m32 $d/main.[ci] -o $d/main.gb
    ##   else
    ##     goto-cc $d/main.[ci] -o $d/main.gb
    ##   fi
    ## done

    ## for d in * ; do
    ##   ec=0
    ##   /usr/bin/time -v timeout -k15 900 goto-instrument-slicing --add-library --full-slice $d/main.gb $d/main.slice.gb || ec=$?
    ##   if [ $ec -eq 124 ] || [ $ec -eq 137 ] ; then
    ##     rm -f $d/main.slice.gb
    ##     echo "TIMEOUT"
    ##   elif [ $ec -eq 11 ] ; then
    ##     # Out of memory
    ##     rm -f $d/main.slice.gb
    ##   elif [ $ec -ne 0 ] ; then
    ##     exit 1
    ##   fi
    ##   if [ -f $d/main.slice.gb ] ; then
    ##     goto-instrument-slicing --count-eloc $d/main.gb
    ##     goto-instrument-slicing --count-eloc $d/main.slice.gb
    ##   fi

    ##   ec=0
    ##   ##/usr/bin/time -v timeout -k15 900 goto-instrument --accelerate --z3 $d/main.gb $d/main.accel.gb || ec=$?
    ##   if [ $ec -eq 124 ] || [ $ec -eq 137 ] ; then
    ##     rm -f $d/main.accel.gb
    ##     echo "TIMEOUT"
    ##   elif [ $ec -eq 11 ] ; then
    ##     # Out of memory
    ##     rm -f $d/main.accel.gb
    ##   elif [ $ec -ne 0 ] ; then
    ##     exit 1
    ##   fi
    ## done

    ## for d in * ; do
    ##   if [ -f $d/main.slice.gb ] ; then
    ##     sed -i '2s/main.[ci]/main.slice.gb/' $d/test.desc
    ##   else
    ##     sed -i '1s/CORE/KNOWNBUG/' $d/test.desc
    ##   fi
    ## done

    ## test.pl -j 4 -c "timeout 900 inc.sh"

    ## cd ..
  done
done

