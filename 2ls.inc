# tool

TOOL_BINARY=./2ls-binary
TOOL_NAME=2LS

# function to run the tool

run()
{
  # add property-specific options
  if [[ "$PROP" == "termination" ]]; then
    PROPERTY1="$PROPERTY --termination --competition-mode"
    PROPERTY2="$PROPERTY --nontermination --competition-mode"

    # run the termination and nontermination analysis in parallel
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH --object-bits OBJ_BITS $PROPERTY1 \
      --function $ENTRY $BM >> $LOG.ok1 2>&1 &
    PID1="$!"
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH --object-bits OBJ_BITS $PROPERTY2 \
      --function $ENTRY $BM >> $LOG.ok2 2>&1 &
    PID2="$!"
    # this might not work in all environments
    wait -n &> /dev/null

    # store the exit code of the first process that is finished
    EC=$?

    # find out which one has finished
    for pid in $PID1 $PID2
    do
      if ! ps -p $pid &> /dev/null; then
        EXITED=$pid
        break
      fi
    done

    # if the result of the first exiting analysis is inconclusive
    # then wait for the other analysis to finish
    if [ $EC -eq 5 ]; then
      wait -n &> /dev/null
      EC=$?
      if [[ "$EXITED" == "$PID1" ]]; then
        mv $LOG.ok2 $LOG.ok
      else
        mv $LOG.ok1 $LOG.ok
      fi
    else # we have a conclusive result, kill the other process
      if [[ "$EXITED" == "$PID1" ]]; then
        kill -9 $PID2 &> /dev/null
        mv $LOG.ok1 $LOG.ok
      else
        kill -9 $PID1  &> /dev/null
        mv $LOG.ok2 $LOG.ok
      fi
    fi
  else
    PROPERTY="$PROPERTY --heap-interval --k-induction --competition-mode"

    # run the tool
    $TOOL_BINARY --graphml-witness $LOG.witness $BIT_WIDTH --object-bits OBJ_BITS $PROPERTY \
      --function $ENTRY $BM >> $LOG.ok 2>&1

    # store the exit code
    EC=$?
  fi
}
