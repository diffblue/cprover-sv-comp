# tool

TOOL_BINARY=./cbmc-binary
TOOL_NAME=CBMC
FIND_OPTIONS=""

# function to run the tool

run()
{
  if [ "$PROP" = "termination" ] ; then
    PROPERTY="$PROPERTY --no-assertions --no-self-loops-to-assumptions"
  fi

  gmon_suffix=$GMON_OUT_PREFIX
  export GMON_OUT_PREFIX="goto-cc_$gmon_suffix"
  ./goto-cc --object-bits $OBJ_BITS --function $ENTRY "${BM[@]}" -o $LOG.bin
  if [ -n "$FAIL_FUNCTION" ]; then
    ./goto-instrument $LOG.bin $LOG.bin --remove-function-body "$FAIL_FUNCTION" \
                                        --generate-function-body "$FAIL_FUNCTION" \
                                        --generate-function-body-options assert-false
  fi

  export GMON_OUT_PREFIX="cbmc_$gmon_suffix"
timeout 875 bash -c ' \
\
ulimit -v 15000000 ; \
\
EC=42 ; \
for c in 2 6 12 17 21 40 200 400 1025 2049 268435456 ; do \
echo "Unwind: $c" > $LOG.latest ; \
./cbmc-binary --no-unwinding-assertions --no-standard-checks --lazy-c-seq-rounds 3 --graphml-witness $LOG.witness --slice-formula --unwind $c --stop-on-fail --object-bits $OBJ_BITS $PROPERTY $LOG.bin >> $LOG.latest 2>&1 ; \
ec=$? ; \
if [ $ec -eq 0 ] ; then \
if ! tail -n 10 $LOG.latest | grep -q "^VERIFICATION SUCCESSFUL$" ; then ec=1 ; else \
./cbmc-binary --lazy-c-seq-rounds 3 --no-standard-checks --slice-formula --unwind $c --stop-on-fail --object-bits $OBJ_BITS $PROPERTY $LOG.bin > /dev/null 2>&1 || ec=42 ; \
fi ; \
fi ; \
if [ $ec -eq 10 ] ; then \
if ! tail -n 10 $LOG.latest | grep -q "^VERIFICATION FAILED$" ; then ec=1 ; fi ; \
fi ; \
\
case $ec in \
0) EC=0 ; mv $LOG.latest $LOG.ok ; echo "EC=$EC" >> $LOG.ok ; break ;; \
10) EC=10 ; mv $LOG.latest $LOG.ok ; echo "EC=$EC" >> $LOG.ok ; break ;; \
42) EC=42 ; mv $LOG.latest $LOG.ok ; echo "EC=$EC" >> $LOG.ok ;; \
*) if [ $EC -ne 0 ] ; then EC=$ec ; mv $LOG.latest $LOG.ok ; fi ; echo "EC=$EC" >> $LOG.ok ; break ;; \
esac ; \
\
done \
'
  if [ ! -s $LOG.ok ] ; then
    mv $LOG.latest $LOG.ok ; echo "EC=42" >> $LOG.ok
  fi
  eval `tail -n 1 $LOG.ok`
}
