# tool

TOOL_BINARY=./jbmc-binary
TOOL_NAME=JBMC
FIND_OPTIONS="-name '*.java'"
JVM_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# function to run the tool

run()
{
  mkdir -p $BM_DIR/classes
  mkdir -p $BM_DIR/src/org/sosy_lab/sv_benchmarks
  HAS_NONDET=0
  # We have to patch the Verifier interface.
  # Should be upstreamed to sv-benchmarks to make witness checking easier.
  # Make a copy of Verifier.java.
  for f in "${!BM[@]}"; do
    echo "${BM[$f]}" | grep Verifier.java > /dev/null
    if [ $? -eq 0 ] ; then
      VERIFIER_FILE="$BM_DIR/src/org/sosy_lab/sv_benchmarks/Verifier.java"
      cp "${BM[$f]}" $VERIFIER_FILE
      BM[$f]="$VERIFIER_FILE"
    else
      grep "Verifier.nondet" "${BM[$f]}" > /dev/null
      if [ $? -eq 0 ] ; then
        HAS_NONDET=1
      fi
    fi
  done
  # We have to distinguish assumption from assertion failures.
  sed -i 's/Runtime.getRuntime().halt(1);/Runtime.getRuntime().halt(2);/g' $VERIFIER_FILE
  # Let's determinize (uses same inputs for all benchmarks).
  sed -i 's/new Random().nextInt()/11/g' $VERIFIER_FILE
  sed -i 's/new Random().nextBoolean()/false/g' $VERIFIER_FILE
  sed -i 's/new Random().nextLong()/11/g' $VERIFIER_FILE
  sed -i 's/new Random().nextFloat()/11.0f/g' $VERIFIER_FILE
  sed -i 's/new Random().nextDouble()/11.0/g' $VERIFIER_FILE
  sed -i 's/int size = random.nextInt();/int size = 1;/g' $VERIFIER_FILE
  sed -i 's/return new String(bytes);/return "JBMC at SV-COMP 2022";/g' $VERIFIER_FILE
  # Compile
  $JVM_HOME/bin/javac -g -cp $BM_DIR/classes -d $BM_DIR/classes "${BM[@]}"
  # Check whether the file runs
  timeout 10 $JVM_HOME/bin/java -ea -cp $BM_DIR/classes Main >> $LOG.latest 2>&1
  ECR=$?
  EC=42
  # Filter out memouts and other errors
  if [ $ECR -eq 1 ] ; then
    grep -E "java\.lang\.StackOverflowError|java\.lang\.OutOfMemoryError|Error: Could not find or load main class|Error: Main method not found in class|Exception in thread \"main\" java\..*Exception" $LOG.latest > /dev/null
    if [ $? -eq 0 ] ; then
      ECR=42
    fi
  fi
  # Assertion failure found
  if [ $ECR -eq 1 ] ; then
    EC=10
    mv $LOG.latest $LOG.ok
    echo "EC=$EC" >> $LOG.ok
  fi
  # No assertion failure, but deterministic
  if [ $ECR -eq 0 ] ; then
    if [ $HAS_NONDET -eq 0 ] ; then
      EC=0
      mv $LOG.latest $LOG.ok
      echo "EC=$EC" >> $LOG.ok
    fi
  fi
  if [ $EC -eq 42 ]; then
    rm $BM_DIR/classes/org/sosy_lab/sv_benchmarks/Verifier.class
    jar -cfe $BM_DIR/task.jar Main -C $BM_DIR/classes .
    export TASK="$BM_DIR/task.jar"

    export MORE_OPTIONS="--java-threading --throw-runtime-exceptions --max-nondet-string-length 100 --classpath core-models.jar:cprover-api.jar"

    if [ "$PROP" = "termination" ] ; then
      PROPERTY="$PROPERTY --no-assertions --no-self-loops-to-assumptions"
    fi

    timeout 875 bash -c ' \
\
ulimit -v 15000000 ; \
\
EC=42 ; \
for c in 2 6 10 15 20 25 30 35 45 60 100 150 200 300 400 500 1025 2049 268435456 ; do \
echo "Unwind: $c" > $LOG.latest ; \
./jbmc-binary $MORE_OPTIONS --graphml-witness $LOG.witness --unwind $c --stop-on-fail --$BIT_WIDTH --object-bits $OBJ_BITS $PROPERTY --function $ENTRY -jar $TASK >> $LOG.latest 2>&1 ; \
ec=$? ; \
if [ $ec -eq 0 ] ; then \
if ! tail -n 10 $LOG.latest | grep -q "^VERIFICATION SUCCESSFUL$" ; then ec=1 ; else \
./jbmc-binary $MORE_OPTIONS --unwinding-assertions --unwind $c --stop-on-fail --$BIT_WIDTH --object-bits $OBJ_BITS $PROPERTY --function $ENTRY -jar $TASK > /dev/null 2>&1 || ec=42 ; \
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
  fi
  eval `tail -n 1 $LOG.ok`
}
