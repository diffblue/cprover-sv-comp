#!/bin/bash

CONFIG=$1

case $CONFIG in
  2ls)
    TOOL=2ls
    REPO=2ls
    ;;
  cbmc|cbmc-path)
    TOOL=cbmc
    REPO=cbmc
    ;;
  jbmc)
    TOOL=jbmc
    REPO=cbmc
    ;;
  *)
    echo "Unknown configuration $CONFIG" 1>&2
    exit 1
    ;;
esac

cat <<EOF
CPROVER is a framework of software analysis tools. See https://www.cprover.org/
for further information about the tools, publications, and the pointers to
source code.

This archive contains the following files:

EOF

if [ x$TOOL != xjbmc ]
then
  cat <<EOF
- goto-cc: this C compiler transforms input files into so-called
  "goto-binaries," which are encoded in CBMC's intermediate representation.

- $TOOL-binary: this is the actual verification tool. It takes a goto-binary or
  source code as input and checks the properties specified by command-line
  flags.

- $TOOL: this wrapper script invokes $TOOL-binary and goto-cc, parsing the
  property file to pass the correct flags to $TOOL-binary and returning the
  correct return codes for SV-COMP.
EOF
else
  cat <<EOF
- jbmc-binary: this is the actual verification tool. It takes Java bytecode
  (class files) as input and checks the properties specified by command-line
  flags.

- jbmc: this wrapper script invokes jbmc-binary, parsing the property file to
  pass the correct flags to jbmc-binary and returning the correct return codes
  for SV-COMP.
EOF
fi

cat <<EOF

The binaries were compiled on $(lsb_release -d -s); the binaries
should be self-hosting on similar operating systems.  The upstream URL, if
you wish to compile it yourself, is https://github.com/diffblue/$REPO
EOF

if [ x$CONFIG = xcbmc-path ]
then
  cat <<EOF

To run CBMC Path manually, you need to invoke the tool as

    cbmc-binary --paths fifo ...

which activates CBMC's path-exploration mode. Note that the tool will not
terminate for input programs that contain loops unless you specify an
unwinding limit using --unwind N. For other flags, see `cbmc-binary -h`.

EOF
elif [ x$TOOL != xjbmc ]
then
  cat <<EOF

To use the tool, run the tool passing a source file as argument. For C source
code, and as only installation requirement, make sure a C compiler (such as GCC)
is installed.
EOF
else
  cat <<EOF

To use the tool, run the tool passing a class or jar file as argument.
Compile sources with Java 8. Using -g is recommended to obtain more
readable counterexample traces.
EOF
fi

cat <<EOF

For SV-COMP, use the wrapper script provided in this distribution, which takes
the following options:
  <path(s)> to sources
  --32 or --64: set the bit width
  --propertyfile <file>: read SV-COMP property specification from <file>
  --graphml-witness <file>: write SV-COMP witness to <file>
EOF
