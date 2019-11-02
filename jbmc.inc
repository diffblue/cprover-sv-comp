# tool

TOOL_BINARY=./jbmc-binary
TOOL_NAME=JBMC
FIND_OPTIONS="-name '*.java'"

# function to run the tool

run()
{
  mkdir -p $BM_DIR/classes
  /usr/lib/jvm/java-8-openjdk-amd64/bin/javac -g -cp $BM_DIR/classes -d $BM_DIR/classes "${BM[@]}"
  rm $BM_DIR/classes/org/sosy_lab/sv_benchmarks/Verifier.class
  jar -cfe $BM_DIR/task.jar Main -C $BM_DIR/classes .
  export TASK="$BM_DIR/task.jar"

  export MORE_OPTIONS="--java-threading --throw-runtime-exceptions --max-nondet-string-length 100 --classpath core-models.jar"

  if [ "$PROP" = "termination" ] ; then
    PROPERTY="$PROPERTY --no-assertions --no-self-loops-to-assumptions"
  fi

timeout 875 bash -c ' \
\
ulimit -v 15000000 ; \
\
EC=42 ; \
for c in 2 6 12 17 21 40 200 400 1025 2049 268435456 ; do \
echo "Unwind: $c" > $LOG.latest ; \
./jbmc-binary $MORE_OPTIONS --graphml-witness $LOG.witness --unwind $c --stop-on-fail --$BIT_WIDTH --object-bits $OBJ_BITS $PROPERTY --function $ENTRY $TASK >> $LOG.latest 2>&1 ; \
ec=$? ; \
if [ $ec -eq 0 ] ; then \
if ! tail -n 10 $LOG.latest | grep -q "^VERIFICATION SUCCESSFUL$" ; then ec=1 ; else \
./jbmc-binary $MORE_OPTIONS --unwinding-assertions --unwind $c --stop-on-fail --$BIT_WIDTH --object-bits $OBJ_BITS $PROPERTY --function $ENTRY $TASK > /dev/null 2>&1 || ec=42 ; \
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
