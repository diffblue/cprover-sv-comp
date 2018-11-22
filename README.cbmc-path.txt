                           CBMC Path
                           =========

This archive contains the following files:

- goto-cc: this C compiler transforms input files into so-called
  `goto-binaries,' which are encoded in CBMC's intermediate representation.

- cbmc-binary: this is the actual verification tool. It takes a goto-binary
  as input and checks the properties specified by command-line flags.

- cbmc: this wrapper script invokes cbmc-binary and goto-cc, parsing the
  property file to pass the correct flags to cbmc-binary and returning the
  correct return codes for SV-COMP.

goto-cc and cbmc-binary were compiled on Debian 9 (stretch); the binaries
should be self-hosting on similar operating systems.  The upstream URL, if
you wish to compile it yourself, is https://github.com/diffblue/cbmc

To run CBMC Path manually, you need to invoke the tool as

    cbmc-binary --paths fifo ...

which activates CBMC's path-exploration mode. Note that the tool will not
terminate for input programs that contain loops unless you specify an
unwinding limit using --unwind N. For other flags, see `cbmc-binary -h`.
