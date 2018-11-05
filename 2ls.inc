# tool

TOOL_BINARY=./2ls-binary
TOOL_NAME=2LS
FIND_OPTIONS=""

# function to run the tool

run()
{
  gmon_suffix=$GMON_OUT_PREFIX
  export GMON_OUT_PREFIX="goto-cc_$gmon_suffix"
  ./goto-cc -m$BIT_WIDTH --function $ENTRY "${BM[@]}" -o $LOG.bin

  export GMON_OUT_PREFIX="2ls_$gmon_suffix"
  # add property-specific options
  if [[ "$PROP" == "termination" ]]; then
    PROPERTY1="$PROPERTY --termination --competition-mode"
    PROPERTY2="$PROPERTY --nontermination --competition-mode"

    # run the termination and nontermination analysis in parallel
    $TOOL_BINARY --graphml-witness $LOG.witness --object-bits $OBJ_BITS $PROPERTY1 \
      $LOG.bin >> $LOG.ok1 2>&1 &
    PID1="$!"
    $TOOL_BINARY --graphml-witness $LOG.witness --object-bits $OBJ_BITS $PROPERTY2 \
      $LOG.bin >> $LOG.ok2 2>&1 &
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
    $TOOL_BINARY --graphml-witness $LOG.witness --object-bits $OBJ_BITS $PROPERTY \
      $LOG.bin >> $LOG.ok 2>&1

    # store the exit code
    EC=$?
  fi
}
