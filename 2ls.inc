# tool 

TOOL_BINARY=./2ls-binary
TOOL_NAME=2LS

# function to run the tool

run() 
{
  # add property-specific options
  if [[ "$PROP" == "termination" ]]; then
    PROPERTY="$PROPERTY --termination --competition-mode"
  else
    PROPERTY="$PROPERTY --k-induction --competition-mode"
  fi

  # run the tool
  $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY \
    --function $ENTRY $BM >> $LOG.ok 2>&1

  # store the exit code
  EC=$?
}
