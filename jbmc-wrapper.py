#!/usr/bin/env python3

import sys
from jbmc import JBMCWrapper

if __name__ == "__main__":
    wrapper = JBMCWrapper()
    wrapper.parse_arguments(sys.argv[1:])
    wrapper.execute()