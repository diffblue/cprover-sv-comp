#!/bin/bash
set -e

sudo chmod o+wt '/sys/fs/cgroup/cpuset/'
sudo chmod o+wt '/sys/fs/cgroup/cpu,cpuacct/user.slice'
sudo chmod o+wt '/sys/fs/cgroup/freezer/'
sudo chmod o+wt '/sys/fs/cgroup/memory/user.slice'

LOG=~/www/public/log.txt
PROGRESS=~/www/public/log

PUBLIC_DIR=~/www/public

REPO=https://github.com/nmanthey/cbmc
#https://github.com/diffblue/cbmc.git 

#CBMC versions:
# cbmc-5.8
# 2017/09 02ed3bf4337d4e40491c34f01fe8d081b4d3d8c6
# 2017/10 897aaf640ef97d9e09b2073e02eac93a7a452ff7
# 2017/11 b67d6e80fd66619e4bc0bf400de1e3c5beec30d8
# cbmc-sv-comp-2018
# 2017/12 b9372f1ae399b2636c60597510a4d08ff16d8038
# 2018/01 2d67e42572f2d4d1966466edb8613245ea8d94b6
# 2018/02 4a93a29a10f43dc27766c8d785b85e772127e254
# 2018/03 4dd0f29734d7d5d1a08f426ccf88883cc375096c
# 2018/04 988b81841441afb8c3eb1d4cdfb72d7e501297ff
# 2018/05 e0bc5fd941d497ad6f55dcdac90fee8f841aa36f
# 2018/06 3f951dd60532c63b72eb878931dd2c3119d56b0f
# cbmc-5.9
# 2018/07 ffbb83fdce4c4ba10b3ec916d91b9c9b32cc5be8
# 2018/08 80331d8a57e526ab09d0c108617f831e69a4aba8
# cbmc-5.10
# 2018/09 d733fe34e1ce270738468d00e30bc16849f9a640
# 2018/10 22e9fa80c3305944ff94f085361d8a1c4eeba074
# 2018/11 25d5bff49bdba335bbc124b3c2a333338456edd1
# manthey-minisat-base 9494ebe92f6f98ddb7bdc9f32bcbb04adcf6e191
# manthey-minisat-enhanced 8640288
# manthey-glucose-enhanced
# mantehy-glucose-fully-enhanced

cd cprover-sv-comp >> $LOG 2>&1
make cbmc-wrapper >> $LOG 2>&1
cd ../benchexec >> $LOG 2>&1
cp ../cprover-sv-comp/cbmc-wrapper cbmc >> $LOG 2>&1
cp ../sv-comp/benchmark-defs/cbmc.xml . >> $LOG 2>&1
#echo "`date` Benchexec wrappers set up" | tee -a $PROGRESS $LOG
for v in 8640288-glucose-fully-enhanced
#22e9fa80c3305944ff94f085361d8a1c4eeba074 25d5bff49bdba335bbc124b3c2a333338456edd1
# 02ed3bf4337d4e40491c34f01fe8d081b4d3d8c6 897aaf640ef97d9e09b2073e02eac93a7a452ff7 b67d6e80fd66619e4bc0bf400de1e3c5beec30d8 b9372f1ae399b2636c60597510a4d08ff16d8038 2d67e42572f2d4d1966466edb8613245ea8d94b6 4a93a29a10f43dc27766c8d785b85e772127e254 4dd0f29734d7d5d1a08f426ccf88883cc375096c 988b81841441afb8c3eb1d4cdfb72d7e501297ff e0bc5fd941d497ad6f55dcdac90fee8f841aa36f 3f951dd60532c63b72eb878931dd2c3119d56b0f ffbb83fdce4c4ba10b3ec916d91b9c9b32cc5be8 80331d8a57e526ab09d0c108617f831e69a4aba8 22e9fa80c3305944ff94f085361d8a1c4eeba074
do
#echo "`date` Updating CBMC" | tee -a $PROGRESS $LOG
#rm -Rf ../cbmc >> $LOG 2>&1
#git clone $REPO ../cbmc >> $LOG 2>&1
#cd ../cbmc/src >> $LOG 2>&1
#git checkout $v >> $LOG 2>&1
#rm -f sha.txt
#git log | head -n 1 | cut -c 8- > sha.txt
#SHA=`cat sha.txt`
SHA=$v
echo "`date` CBMC commit $SHA" | tee -a $PROGRESS $LOG
#echo "`date` Compiling CBMC" | tee -a $PROGRESS $LOG
#make clean >> $LOG 2>&1
#make minisat2-download >> $LOG 2>&1
#make -j4 >> $LOG 2>&1
rm -f version.txt
#cbmc/cbmc --version | cut -c-4 | tr -d '[:space:]' > version.txt
./cbmc --version | cut -c-4 | tr -d '[:space:]' > version.txt
#CDATE=`git show -s --format=%ci | cut -c-10`
CDATE="2018-11-09"
TIMESTAMP_FILE="${CDATE}_0000"
TIMESTAMP_TEXT="${CDATE} 00:00:00 UTC"
echo "`date` CBMC version `cat version.txt`" | tee -a $PROGRESS $LOG
echo "`date` Preparing CBMC for benchexec" | tee -a $PROGRESS $LOG
#cd ../../benchexec >> $LOG 2>&1
#cp ../cbmc/src/cbmc/cbmc cbmc-binary >> $LOG 2>&1
VERSION=`cat ../cbmc/src/version.txt`
VERSION=`cat version.txt`
cp ../cprover-sv-comp/cbmc-wrapper cbmc >> $LOG 2>&1
sed -i.bak "s/\$TOOL_BINARY --version/echo ${VERSION}-${SHA}/g" cbmc
for TASK in ReachSafety-Arrays ReachSafety-BitVectors ReachSafety-ControlFlow ReachSafety-Loops MemSafety-Arrays MemSafety-Heap MemSafety-LinkedLists ReachSafety-Floats ReachSafety-Heap
do
OUTPUT_DIR="results-$TASK"
echo "`date` Starting evaluation for $TASK $TIMESTAMP_TEXT" | tee -a $PROGRESS $LOG
rm -f results/* >> $LOG 2>&1
bin/benchexec cbmc.xml --no-container -t $TASK >> $LOG 2>&1
echo "`date` Evaluation finished, updating tables" | tee -a $PROGRESS $LOG
cd results
../../rename.sh "$TIMESTAMP_FILE" "$TIMESTAMP_TEXT" >> $LOG 2>&1
cd ..
mv results/*.zip $OUTPUT_DIR/ >> $LOG 2>&1
mv results/*.xml.bz2 $OUTPUT_DIR/ >> $LOG 2>&1
rm -f $OUTPUT_DIR/*.html >> $LOG 2>&1
rm -f $OUTPUT_DIR/*.csv >> $LOG 2>&1
bin/table-generator $OUTPUT_DIR/*.xml.bz2 >> $LOG 2>&1
pwd >> $LOG 2>&1
ls $OUTPUT_DIR >> $LOG 2>&1
cp $OUTPUT_DIR/*.zip $PUBLIC_DIR/benchexec/$OUTPUT_DIR/ >> $LOG 2>&1
cp $OUTPUT_DIR/*.xml.bz2 $PUBLIC_DIR/benchexec/$OUTPUT_DIR/ >> $LOG 2>&1
cp $OUTPUT_DIR/*table.html $PUBLIC_DIR/benchexec/$OUTPUT_DIR/index.html >> $LOG 2>&1
cp $OUTPUT_DIR/*diff.html $PUBLIC_DIR/benchexec/$OUTPUT_DIR/diff.html >> $LOG 2>&1
echo "`date` Done" | tee -a $PROGRESS $LOG
done
done
