# tool 

TOOL_BINARY=./2ls-binary
TOOL_NAME=2LS

# function to run the tool

run() 
{
  # add property-specific options
  if [[ "$PROP" == "termination" ]]; then
    PROPERTY="$PROPERTY --termination --competition-mode"
    PROPERTY2="$PROPERTY --nontermination --competition-mode"
    
    # run the tool
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY \
      --function $ENTRY $BM >> $LOG.ok 2>&1 #&
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY2 \
      --function $ENTRY $BM >> $LOG.ok 2>&1 &
    wait -n
    
    EC=$?
    
    if [$EC -eq 5]; then
      wait $!
      EC=$?
    fi
  else
    PROPERTY="$PROPERTY --k-induction --competition-mode"
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY \
    --function $ENTRY $BM >> $LOG.ok 2>&1
    EC=$?
    # store the exit code
  fi
}
