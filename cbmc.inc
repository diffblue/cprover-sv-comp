# tool 

TOOL_BINARY=./cbmc-binary
TOOL_NAME=CBMC

# function to run the tool

run() 
{
timeout 850 bash -c ' \
\
ulimit -v 15000000 ; \
\
EC=42 ; \
for c in 2 6 12 17 21 40 200 400 1025 2049 268435456 ; do \
echo "Unwind: $c" > $LOG.latest ; \
./cbmc-binary --graphml-witness $LOG.witness --unwind $c --stop-on-fail $BIT_WIDTH $PROPERTY --function $ENTRY $BM >> $LOG.latest 2>&1 ; \
ec=$? ; \
if [ $ec -eq 0 ] ; then \
if ! tail -n 10 $LOG.latest | grep -q "^VERIFICATION SUCCESSFUL$" ; then ec=1 ; else \
./cbmc-binary --unwinding-assertions --unwind $c --stop-on-fail $BIT_WIDTH $PROPERTY --function $ENTRY $BM > /dev/null 2>&1 || ec=42 ; \
fi ; \
fi ; \
if [ $ec -eq 10 ] ; then \
if ! tail -n 10 $LOG.latest | grep -q "^VERIFICATION FAILED$" ; then ec=1 ; fi ; \
fi ; \
\
case $ec in \
0) EC=0 ; mv $LOG.latest $LOG.ok ; echo "EC=$EC" >> $LOG.ok ;; \
10) EC=10 ; mv $LOG.latest $LOG.ok ; echo "EC=$EC" >> $LOG.ok ; break ;; \
42) EC=42 ; mv $LOG.latest $LOG.ok ; echo "EC=$EC" >> $LOG.ok ;; \
*) if [ $EC -ne 0 ] ; then EC=$ec ; mv $LOG.latest $LOG.ok ; fi ; echo "EC=$EC" >> $LOG.ok ; break ;; \
esac ; \
\
done \
'
  eval `tail -n 1 $LOG.ok`
}
