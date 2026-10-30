#!/usr/bin/env python3

import unittest
import sys
import os
import tempfile
import hashlib
import shutil
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tool_wrapper import (
    complete_yaml_witness, find_input_file, make_yaml_witness,
    nondet_call_columns, violated_specification)
from jbmc_wrapper import JBMCWrapper, NONDET_LOG_PREFIX
from cbmc_wrapper import CBMCWrapper


C_WITNESS = '''- entry_type: "violation_sequence"
  metadata:
    format_version: "2.0"
    uuid: "724d13a1-c81f-43bc-8ced-8826e7b0b30a"
    creation_time: "2026-10-30T09:58:47Z"
    producer:
      name: "CBMC"
      version: "6.11.0"
    task:
      data_model: "LP64"
      language: "C"
  content:
  - segment:
    - waypoint:
        type: "function_return"
        action: "follow"
        constraint:
          value: "\\\\result == 1"
          format: "acsl_expression"
        location:
          file_name: "main.c"
          line: 4
          function: "main"
  - segment:
    - waypoint:
        type: "function_return"
        action: "follow"
        constraint:
          value: "\\\\result == 2"
          format: "acsl_expression"
        location:
          file_name: "main.c"
          line: 4
          function: "main"
  - segment:
    - waypoint:
        type: "function_return"
        action: "follow"
        constraint:
          value: "\\\\result == 3"
          format: "acsl_expression"
        location:
          file_name: "header.h"
          line: 1
          function: "f"
  - segment:
    - waypoint:
        type: "target"
        action: "follow"
        location:
          file_name: "main.c"
          line: 6
          function: "main"
'''

C_PROGRAM = '''int __VERIFIER_nondet_int(void);
int main()
{
  int a = __VERIFIER_nondet_int(), b = __VERIFIER_nondet_int();
  if(a == 1 && b == 2)
    { reach_error(); }
}
'''


class TestProcessYAML(unittest.TestCase):
    """Test cases for completing YAML witnesses"""

    def setUp(self):
        self.cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        self.c_file = os.path.join(self.temp_dir, "main.c")
        with open(self.c_file, 'w') as f:
            f.write(C_PROGRAM)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_dir)

    def test_nondet_call_columns_c(self):
        line = "  int a = __VERIFIER_nondet_int(), b = __VERIFIER_nondet_int();"
        self.assertEqual(nondet_call_columns(line, "C"), [33, 62])

    def test_nondet_call_columns_java(self):
        line = "    int x = add(Verifier.nondetInt(), Verifier.nondetInt());"
        self.assertEqual(nondet_call_columns(line, "Java"), [35, 57])

    def test_find_input_file(self):
        input_files = ["./java/common/org/sosy_lab/sv_benchmarks/Verifier.java",
                       "./java/task/Main.java", "./java/task/pkg/Main.java"]
        self.assertEqual(find_input_file("Main.java", input_files),
                         "./java/task/Main.java")
        self.assertEqual(find_input_file("pkg/Main.java", input_files),
                         "./java/task/pkg/Main.java")
        self.assertEqual(
            find_input_file("org/sosy_lab/sv_benchmarks/Verifier.java", input_files),
            input_files[0])
        self.assertIsNone(find_input_file("java/lang/Integer.java", input_files))

    def test_violated_specification(self):
        memsafety = ("CHECK( init(main()), LTL(G valid-free) )\n"
                     "CHECK( init(main()), LTL(G valid-deref) )\n"
                     "CHECK( init(main()), LTL(G valid-memtrack) )\n")
        self.assertEqual(violated_specification(memsafety, "FALSE(valid-deref)"),
                         "CHECK( init(main()), LTL(G valid-deref) )")
        unreach = "CHECK( init(main()), LTL(G ! call(reach_error())) )\n"
        self.assertEqual(violated_specification(unreach, "FALSE"), unreach.strip())

    def test_complete_c_witness(self):
        os.chdir(self.temp_dir)
        witness = complete_yaml_witness(
            C_WITNESS, ["main.c"], "CHECK( init(main()), LTL(G ! call(reach_error())) )",
            "reach_error")

        with open(self.c_file, 'rb') as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        self.assertIn('    task:\n      input_files:\n      - "main.c"\n', witness)
        self.assertIn(f'        "main.c": "{digest}"\n', witness)
        self.assertIn(
            '      specification: "CHECK( init(main()), LTL(G ! call(reach_error())) )"\n'
            '      data_model: "LP64"\n', witness)
        # the two calls on line 4 get the columns of their closing parentheses
        self.assertIn('          line: 4\n          column: 33\n', witness)
        self.assertIn('          line: 4\n          column: 62\n', witness)
        # waypoints outside the input files are dropped
        self.assertNotIn('header.h', witness)
        self.assertNotIn('\\\\result == 3', witness)
        # the target points to the call of reach_error
        self.assertIn('          line: 6\n          column: 7\n', witness)

    def test_complete_producer_version(self):
        os.chdir(self.temp_dir)
        witness = complete_yaml_witness(
            C_WITNESS, ["main.c"], "CHECK( init(main()), LTL(G ! call(reach_error())) )",
            "reach_error", producer_version="6.11.0 (+ cprover-sv-comp-0123456789)")
        self.assertIn('      name: "CBMC"\n'
                      '      version: "6.11.0 (+ cprover-sv-comp-0123456789)"\n', witness)
        self.assertNotIn('"6.11.0"', witness)

    def test_make_yaml_witness(self):
        witness = make_yaml_witness("JBMC", "6.11.0", "Java", [
            {"type": "function_return", "file_name": "Main.java", "line": 5,
             "value": "11L"},
            {"type": "target", "file_name": "Main.java", "line": 7},
        ])
        self.assertIn('    format_version: "2.4"\n', witness)
        self.assertIn('    task:\n      language: "Java"\n', witness)
        self.assertIn('          value: "\\\\result == 11L"\n'
                      '          format: "ext_java_expression"\n', witness)
        self.assertIn('        type: "target"\n', witness)

    def test_correctness_witness(self):
        os.chdir(self.temp_dir)
        prop_file = os.path.join(self.temp_dir, "unreach-call.prp")
        with open(prop_file, 'w') as f:
            f.write("CHECK( init(main()), LTL(G ! call(reach_error())) )\n")
        wrapper = CBMCWrapper()
        wrapper.prop_file = prop_file
        wrapper.input_files = ["main.c"]
        wrapper.bit_width = "32"
        with patch.object(wrapper, "tool_version", return_value="6.11.0 (cbmc-6.11.0)"):
            witness = wrapper.process_yaml(0, None)
        self.assertTrue(witness.startswith('- entry_type: "invariant_set"\n'))
        self.assertIn('      version: "6.11.0 (cbmc-6.11.0 + cprover-sv-comp-', witness)
        self.assertIn('    format_version: "2.0"\n', witness)
        self.assertIn('      - "main.c"\n', witness)
        self.assertIn(
            '      specification: "CHECK( init(main()), LTL(G ! call(reach_error())) )"\n'
            '      data_model: "ILP32"\n'
            '      language: "C"\n'
            '  content: []\n', witness)

    def test_tool_and_wrapper_version(self):
        wrapper = CBMCWrapper()
        with patch.object(wrapper, "tool_version",
                          return_value="6.11.0 (cbmc-6.11.0-47-g41dc048b07)"):
            self.assertRegex(
                wrapper.tool_and_wrapper_version(),
                r"^6\.11\.0 \(cbmc-6\.11\.0-47-g41dc048b07 \+ cprover-sv-comp-\S+\)$")
        with patch.object(wrapper, "tool_version", return_value="0.1"):
            self.assertRegex(
                wrapper.tool_and_wrapper_version(), r"^0\.1 \+ cprover-sv-comp-\S+$")

    def test_instrument_verifier(self):
        verifier = ("package org.sosy_lab.sv_benchmarks;\n"
                    "public final class Verifier {\n"
                    "  public static int nondetInt() {\n"
                    "    return 11;\n"
                    "  }\n"
                    "}\n")
        instrumented = JBMCWrapper._instrument_verifier(verifier)
        lines = instrumented.splitlines()
        self.assertIn("public static int nondetInt() {", lines[2])
        self.assertIn("private static int __cprover_nondetInt() {", lines[2])
        self.assertEqual(lines[3], "    return 11;")
        self.assertIn("__cproverWitnessValue(long v)", instrumented)
        self.assertTrue(instrumented.rstrip().endswith("}"))

    def test_violation_waypoints(self):
        wrapper = JBMCWrapper()
        wrapper.input_files = ["task/Main.java", "task/pkg/Helper.java"]
        log = (f"{NONDET_LOG_PREFIX}\tMain.java\t6\t11\n"
               f"{NONDET_LOG_PREFIX}\tpkg/Helper.java\t7\t11L\n"
               'Exception in thread "main" java.lang.AssertionError\n'
               "\tat java.base/java.util.Objects.requireNonNull(Objects.java:209)\n"
               "\tat pkg.Helper.check(Helper.java:9)\n"
               "\tat Main.main(Main.java:8)\n")
        self.assertEqual(wrapper._violation_waypoints(log), [
            {"type": "function_return", "file_name": "Main.java", "line": 6,
             "value": "11"},
            {"type": "function_return", "file_name": "pkg/Helper.java", "line": 7,
             "value": "11L"},
            {"type": "target", "file_name": "pkg/Helper.java", "line": 9},
        ])


if __name__ == '__main__':
    unittest.main()
