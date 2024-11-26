#!/bin/bash
set -e

git clone -b 1.17 https://github.com/sosy-lab/benchexec --depth=1
git clone -b svcomp19 https://github.com/sosy-lab/sv-comp --depth=1
git clone -b svcomp19 https://github.com/diffblue/cprover-sv-comp --depth=1
