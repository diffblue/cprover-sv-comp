#!/bin/bash

# Translate SV-COMP tasks into CProver regression tests

set -e

warn()
{
  echo "$1" >&2
}


die()
{
  warn "$1"
  exit 1
}

parse_property_file()
{
  local fn=$1

  cat $fn | sed 's/[[:space:]]//g' | perl -n -e '
if(/^CHECK\(init\((\S+)\(\)\),LTL\(G(\S+)\)\)$/) {
  print "ENTRY=$1\n";
  print "PROPERTY=\"--error-label $1\"\n" if($2 =~ /^!label\((\S+)\)$/);
  print "PROPERTY=\" \"\n" if($2 =~ /^!call\(__VERIFIER_error\(\)\)$/);
  print "PROPERTY=\"--pointer-check --memory-leak-check --bounds-check\"\n" if($2 =~ /^valid-(free|deref|memtrack)$/);
  print "PROPERTY=\"--signed-overflow-check\"\n" if($2 =~ /^!overflow$/);
}'
}

convert()
{
  local category=$1
  local sub_category=$2
  local fn=$3

  ENTRY=""
  PROPERTY=""
  eval `parse_property_file $sub_category.prp`

  if [ "x$ENTRY" = "x" ] ; then
    die "Failed to parse entry function of $fn"
  elif [ "x$PROPERTY" = "x" ] ; then
    warn "Unhandled property in $fn"
    return
  fi

  if [ "x$category" = "xConcurrency" ] ; then
    fn="`echo $fn | sed 's/i$/c/'`"
    if [ ! -s $fn ] ; then
      die "Non-preprocessed file $fn in Concurrency category not found"
    fi
  fi

  local suffix="`echo $fn | sed 's/.*\.//'`"
  if [ "x$suffix" != "xc" ] && [ "x$suffix" != "xi" ] ; then
    die "Failed to determine suffix of $fn"
  fi

  local expected_result=""
  local expected_exitcode=""
  local expect_more=""
  case $fn in
    *_true-valid*) expected_result=SUCCESSFUL ; expect_more=TRUE ; expected_exitcode=0 ;;
    *_true-unreach-call*) expected_result=SUCCESSFUL ; expect_more=TRUE ; expected_exitcode=0 ;;
    *_true-no-overflow*) expected_result=SUCCESSFUL ; expect_more=TRUE ; expected_exitcode=0 ;;
    *_true-termination*) expected_result=SUCCESSFUL ; expect_more=TRUE ; expected_exitcode=0 ;;
    *_false-valid*) expected_result=FAILED ; expect_more=FALSE ; expected_exitcode=10 ;;
    *_false-unreach-call*) expected_result=FAILED ; expect_more=FALSE ; expected_exitcode=10 ;;
    *_false-no-overflow*) expected_result=FAILED ; expect_more=FALSE ; expected_exitcode=10 ;;
    *_false-termination*) expected_result=FAILED ; expect_more=FALSE ; expected_exitcode=10 ;;
  esac
  if [ "x$expected_result" = "x" ] ; then
    warn "Failed to determine expected result of $fn"
    return
  fi
  case $fn in
    *_false-valid-memtrack.*) expect_more="$expect_more(valid-memtrack)" ;;
    *_false-valid-deref.*) expect_more="$expect_more(valid-deref)" ;;
    *_false-valid-free.*) expect_more="$expect_more(valid-free)" ;;
    *_false-no-overflow.*) expect_more="$expect_more(no-overflow)" ;;
  esac

  local bitwidth=`grep ^Architecture $sub_category.cfg | awk '{print $2}'`

  mkdir -p cprover-regr/$category/$fn
  cp $fn cprover-regr/$category/$fn/main.$suffix

  cat > cprover-regr/$category/$fn/test.desc <<EOF
CORE
main.$suffix
--function $ENTRY $PROPERTY --$bitwidth
^EXIT=$expected_exitcode$
^SIGNAL=0$
^VERIFICATION $expected_result$
^$expect_more$
--
^warning: ignoring
EOF

  if grep -q "^$category/$fn$" ../KNOWNBUG ; then
    sed -i '1s/CORE/KNOWNBUG/' cprover-regr/$category/$fn/test.desc
  fi
}

git clone --depth=1 https://github.com/sosy-lab/sv-benchmarks.git sv-benchmarks.git
cd sv-benchmarks.git/c

rm -rf cprover-regr

for sub_category in *.set ; do
  category=$sub_category
  case $set in
    ArraysMemSafety) category="Arrays" ;;
    ArraysReach) category="Arrays" ;;
    BitVectorsOverflows) category="BitVectors" ;;
    BitVectorsReach) category="BitVectors" ;;
    BusyBox) category="SoftwareSystems" ;;
    ControlFlow) category="ControlFlowInteger" ;;
    DeviceDriversLinux64) category="SoftwareSystems" ;;
    ECA) category="ControlFlowInteger" ;;
    HeapMemSafety) category="HeapManipulation" ;;
    HeapReach) category="HeapManipulation" ;;
    Loops) category="ControlFlowInteger" ;;
    ProductLines) category="ControlFlowInteger" ;;
    Recursive) category="ControlFlowInteger" ;;
    Sequentialized) category="ControlFlowInteger" ;;
    Simple) category="ControlFlowInteger" ;;
    Termination-*) category="Termination" ;;
  esac
  
  for f in `cat $set.set` ; do
    if [ ! -s "$f" ] ; then
      warn "File $f not found"
      continue
    fi
    convert $category $sub_category $f
  done
done

