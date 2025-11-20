#!/usr/bin/env python3

import sys
from cbmc import CBMCWrapper

if __name__ == "__main__":
    wrapper = CBMCWrapper()
    wrapper.parse_arguments(sys.argv[1:])
    wrapper.execute()