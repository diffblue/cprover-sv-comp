
# main tool wrapper script
# run "make <tool>-wrapper" to generate the wrapper script

# map properties to tool options

declare -A OPTIONS
OPTIONS["label"]="--error-label"
OPTIONS["unreach_call"]=""
OPTIONS["termination"]=""
OPTIONS["overflow"]="--signed-overflow-check --no-assertions"
OPTIONS["memsafety"]="--pointer-check --memory-leak-check --bounds-check --no-assertions"

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

parse_result()
{
  if tail -n 50 $LOG.ok | \
      grep -Eq "^(\[.*\] |[[:space:]]*)__CPROVER_memory_leak == NULL$" ; then
    echo 'FALSE(valid-memtrack)'
  elif tail -n 50 $LOG.ok | \
      grep -Eq "^(\[.*\] |[[:space:]]*)dereference failure:" ; then
    echo 'FALSE(valid-deref)'
  elif tail -n 50 $LOG.ok | \
      grep -Eq "^(\[.*\] |[[:space:]]*)array.* upper bound in " ; then
    echo 'FALSE(valid-deref)'
  elif tail -n 50 $LOG.ok | \
      grep -Eq "^(\[.*\] |[[:space:]]*)double free$" ; then
    echo 'FALSE(valid-free)'
  elif tail -n 50 $LOG.ok | \
      grep -Eq "^(\[.*\] |[[:space:]]*)free argument has offset zero$" ; then
    echo 'FALSE(valid-free)'
  elif tail -n 50 $LOG.ok | \
      grep -Eq "^(\[.*\] |[[:space:]]*)arithmetic overflow on signed" ; then
    echo 'FALSE(no-overflow)'
  elif [[ "$PROP" == "termination" ]]; then
    echo 'FALSE(termination)'
  else
    echo FALSE
  fi
}

process_graphml()
{
  if [ -f $LOG.witness ]; then
    if [ $1 -eq 0 ]; then
      TYPE="correctness_witness"
    else
      TYPE="violation_witness"
    fi
    cat $LOG.witness | perl -p -e "s/(<graph edgedefault=\"directed\">)/\$1\\E
      <data key=\"witness-type\">$(echo $TYPE)<\/data>
      <data key=\"producer\">$(echo $TOOL_NAME)<\/data>
      <data key=\"specification\">$(<$PROP_FILE)<\/data>
      <data key=\"programfile\">$(echo $BM | sed 's8/8\\/8g')<\/data>
      <data key=\"programhash\">$(sha1sum $BM | awk '{print $1}')<\/data>
      <data key=\"architecture\">${BIT_WIDTH##--}bit<\/data>\\Q/"
  fi
}

BIT_WIDTH="--64"
BM=""
PROP_FILE=""
WITNESS_FILE=""

while [ -n "$1" ] ; do
  case "$1" in
    --32|--64) BIT_WIDTH="$1" ; shift 1 ;;
    --propertyfile) PROP_FILE="$2" ; shift 2 ;;
    --graphml-witness) WITNESS_FILE="$2" ; shift 2 ;;
    --version) $TOOL_BINARY --version ; exit 0 ;;
    *) BM="$1" ; shift 1 ;;
  esac
done

if [ -z "$BM" ] || [ -z "$PROP_FILE" ] ; then
  echo "Missing benchmark or property file"
  exit 1
fi

if [ ! -s "$BM" ] || [ ! -s "$PROP_FILE" ] ; then
  echo "Empty benchmark or property file"
  exit 1
fi

eval `parse_property_file $PROP_FILE`

if [[ "$PROP" == "" ]]; then
  echo "Unrecognized property specification"
  exit 1
elif [[ "$PROP" == "label" ]]; then
  PROPERTY="${OPTIONS[$PROP]} $LABEL"
else
  PROPERTY=${OPTIONS[$PROP]}
fi

export ENTRY
export PROPERTY
export BIT_WIDTH
export BM
export PROP

export LOG=`mktemp -t ${TOOL_NAME}-log.XXXXXX`
trap "rm -f $LOG $LOG.latest $LOG.ok $LOG.witness" EXIT

run

if [ ! -s $LOG.ok ] ; then
  exit 1
fi

cat $LOG.ok
case $EC in
  0) if [[ "$WITNESS_FILE" != "" ]]; then process_graphml $EC > $WITNESS_FILE; \
fi; echo "TRUE" ;;
  10) if [[ "$WITNESS_FILE" != "" ]]; then process_graphml $EC > $WITNESS_FILE;\
 fi; parse_result ;;
  *) echo "UNKNOWN" ;;
esac
exit $EC
