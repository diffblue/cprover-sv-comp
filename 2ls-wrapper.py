#!/usr/bin/env python3

import sys
import importlib

# Import 2ls module (module names can't start with digits)
twols_module = importlib.import_module('2ls')
TwoLSWrapper = twols_module.TwoLSWrapper

if __name__ == "__main__":
    wrapper = TwoLSWrapper()
    wrapper.parse_arguments(sys.argv[1:])
    wrapper.execute()