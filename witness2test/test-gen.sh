#!/bin/bash

set -e

parse_property_file()
{
  local fn=$1

  cat $fn | sed 's/[[:space:]]//g' | perl -n -e '
if(/^CHECK\(init\((\S+)\(\)\),LTL\((\S+)\)\)$/) {
  print "ENTRY=$1\n";
  print "PROP=\"label\"\nLABEL=\"$1\"\n" if($2 =~ /^G!label\((\S+)\)$/);
  print "PROP=\"unreach_call\"\n" if($2 =~ /^G!call\(__VERIFIER_error\(\)\)$/);
  print "PROP=\"memsafety\"\n" if($2 =~ /^Gvalid-(free|deref|memtrack)$/);
  print "PROP=\"overflow\"\n" if($2 =~ /^G!overflow$/);
  print "PROP=\"termination\"\n" if($2 =~ /^Fend$/);
}'
}

BIT_WIDTH="-m64"
BM=""
PROP_FILE=""
WITNESS_FILE=""

while [ -n "$1" ] ; do
  case "$1" in
    -m32|-m64) BIT_WIDTH="$1" ; shift 1 ;;
    --propertyfile) PROP_FILE="$2" ; shift 2 ;;
    --graphml-witness) WITNESS_FILE="$2" ; shift 2 ;;
    --version) echo "0.1" ; exit 0 ;;
    *) BM="$1" ; shift 1 ;;
  esac
done

if [ -z "$BM" ] || [ ! -s "$BM" ] ; then
  echo "Missing or empty benchmark file $BM"
  exit 1
fi

if [ -z "$PROP_FILE" ] || [ ! -s "$PROP_FILE" ] ; then
  echo "Missing or empty property file $PROP_FILE"
  exit 1
fi

if [ -z "$WITNESS_FILE" ] ; then
  echo "Missing witness file"
  exit 1
fi

if [ ! -s "$WITNESS_FILE" ] ; then
  echo "INVALID WITNESS FILE: witness file $WITNESS_FILE is empty"
  exit 1
fi

eval `parse_property_file $PROP_FILE`

if [ "$PROP" = "" ] ; then
  echo "Unrecognized property specification"
  exit 1
fi

if [ ! -d pycparser-master ] ; then
  wget https://codeload.github.com/eliben/pycparser/zip/master \
    -O pycparser-master.zip
  unzip pycparser-master.zip
fi

SCRIPTDIR=$PWD
DATA=`mktemp -d -t witness.XXXXXX`
trap "rm -rf $DATA" EXIT
# echo $DATA

cp "$WITNESS_FILE" "$BM" $DATA
WITNESS_FILE=`basename "$WITNESS_FILE"`
BM=`basename "$BM"`
cd $DATA
PYTHONPATH=$SCRIPTDIR/pycparser-master \
  python $SCRIPTDIR/process_witness.py \
  $BIT_WIDTH -w "$WITNESS_FILE" -b "$BM" > data
$SCRIPTDIR/TestEnvGenerator.pl < data
ec=0
make -f tester.mk BUILD_FLAGS="$BIT_WIDTH -std=c99" > log 2>&1 || ec=$?
if [ "$PROP" = "unreach_call" ] ; then
  if ! grep -q "tester: .* __VERIFIER_error: Assertion \`0' failed." log ; then
    cat log 1>&2
    echo "$BM: ERROR - failing assertion not found" 1>&2
    if [ $ec -eq 0 ] ; then
      echo "TRUE"
    else
      echo "UNKNOWN"
    fi
    exit 1
  fi
  echo "$BM: OK"
  echo "FALSE"
else
  echo "$BM: property $PROP not yet handled"
  echo "UNKNOWN"
fi

