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
    
    # run the termination and nontermination analysis in parallel
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY \
      --function $ENTRY $BM >> $LOG.ok 2>&1 &
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY2 \
      --function $ENTRY $BM >> $LOG.ok 2>&1 &
    wait -n
    
    # store the exit code of the first process that is finished
    EC=$?
    
    # if the result of termination analysis is unknown,
    # wait for the most recently executed background process,
    # which is nontermination analysis
    if [$EC -eq 5]; then
      wait $!
      EC=$?
    fi
  else
    PROPERTY="$PROPERTY --k-induction --competition-mode"
    
    # run the tool
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH $PROPERTY \
      --function $ENTRY $BM >> $LOG.ok 2>&1
    
    # store the exit code
    EC=$?
  fi
}
