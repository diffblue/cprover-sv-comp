#!/bin/bash
set -e

sudo chmod o+wt '/sys/fs/cgroup/cpuset/'
sudo chmod o+wt '/sys/fs/cgroup/cpu,cpuacct/user.slice'
sudo chmod o+wt '/sys/fs/cgroup/freezer/'
sudo chmod o+wt '/sys/fs/cgroup/memory/user.slice'

LOG=~/www/public/log.txt
PROGRESS=~/www/public/log

PUBLIC_DIR=~/www/public/svcomp19

REPO=https://github.com/diffblue/cbmc.git

cd cprover-sv-comp >> $LOG 2>&1
make cbmc-wrapper >> $LOG 2>&1
cd ../benchexec >> $LOG 2>&1
cp ../cprover-sv-comp/cbmc-wrapper cbmc >> $LOG 2>&1
cp ../sv-comp/benchmark-defs/cbmc.xml . >> $LOG 2>&1
echo "`date` Benchexec wrappers set up" | tee -a $PROGRESS $LOG
for v in 5594db641 e743f02fc eca9b599e
do
echo "`date` Updating CBMC" | tee -a $PROGRESS $LOG
rm -Rf ../cbmc >> $LOG 2>&1
git clone $REPO ../cbmc >> $LOG 2>&1
cd ../cbmc/src >> $LOG 2>&1
git checkout $v >> $LOG 2>&1
rm -f sha.txt
git log | head -n 1 | cut -c 8- > sha.txt
SHA=`cat sha.txt`
echo "`date` CBMC commit $SHA" | tee -a $PROGRESS $LOG
echo "`date` Compiling CBMC" | tee -a $PROGRESS $LOG
make clean >> $LOG 2>&1
make minisat2-download >> $LOG 2>&1
make -j4 >> $LOG 2>&1
rm -f version.txt
cbmc/cbmc --version | cut -c-4 | tr -d '[:space:]' > version.txt
CDATE=`git show -s --format=%ci | cut -c-10`
TIMESTAMP_FILE="${CDATE}_0000"
TIMESTAMP_TEXT="${CDATE} 00:00:00 UTC"
echo "`date` CBMC version `cat version.txt`" | tee -a $PROGRESS $LOG
echo "`date` Preparing CBMC for benchexec" | tee -a $PROGRESS $LOG
cd ../../benchexec >> $LOG 2>&1
cp ../cbmc/src/cbmc/cbmc cbmc-binary >> $LOG 2>&1
cp ../cbmc/src/goto-cc/goto-cc goto-cc >> $LOG 2>&1
VERSION=`cat ../cbmc/src/version.txt`
cp ../cprover-sv-comp/cbmc-wrapper cbmc >> $LOG 2>&1
sed -i.bak "s/\$TOOL_BINARY --version/echo ${VERSION}-${SHA}/g" cbmc
for TASK in ReachSafety-Arrays ReachSafety-BitVectors ReachSafety-ControlFlow  ReachSafety-Floats ReachSafety-Heap ReachSafety-Loops MemSafety-Arrays MemSafety-Heap MemSafety-LinkedLists
do
OUTPUT_DIR="results-$TASK"
echo "`date` Starting evaluation for $TASK $TIMESTAMP_TEXT" | tee -a $PROGRESS $LOG
rm -f results/* >> $LOG 2>&1
bin/benchexec cbmc.xml --no-container -t $TASK >> $LOG 2>&1
echo "`date` Evaluation finished, updating tables" | tee -a $PROGRESS $LOG
cd results
../../rename.sh "$TIMESTAMP_FILE" "$TIMESTAMP_TEXT" >> $LOG 2>&1
cd ..
mkdir -p $OUTPUT_DIR >> $LOG 2>&1
mv results/*.zip $OUTPUT_DIR/ >> $LOG 2>&1
mv results/*.xml.bz2 $OUTPUT_DIR/ >> $LOG 2>&1
rm -f $OUTPUT_DIR/*.html >> $LOG 2>&1
rm -f $OUTPUT_DIR/*.csv >> $LOG 2>&1
bin/table-generator $OUTPUT_DIR/*.xml.bz2 >> $LOG 2>&1
pwd >> $LOG 2>&1
ls $OUTPUT_DIR >> $LOG 2>&1
mkdir -p $PUBLIC_DIR/benchexec/$OUTPUT_DIR >> $LOG 2>&1
for f in `find $OUTPUT_DIR -name '*.html'`; do cp $f $PUBLIC_DIR/benchexec/$OUTPUT_DIR/index.html >> $LOG 2>&1; done
for f in `find $OUTPUT_DIR -name '*table.html'`; do cp $f $PUBLIC_DIR/benchexec/$OUTPUT_DIR/index.html >> $LOG 2>&1; done
for f in `find $OUTPUT_DIR -name '*diff.html'`; do cp $f $PUBLIC_DIR/benchexec/$OUTPUT_DIR/diff.html >> $LOG 2>&1; done
echo "`date` Done" | tee -a $PROGRESS $LOG
done
done
