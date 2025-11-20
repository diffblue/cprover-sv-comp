#!/usr/bin/env python3

import unittest
import subprocess
import tempfile
import os
import sys
# Add parent directory to path to import the wrapper modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cbmc_wrapper import CBMCWrapper


class TestParsePropertyFile(unittest.TestCase):
    def setUp(self):
        self.wrapper = CBMCWrapper()

    def run_parse_property_file(self, content):
        # Write content to a temporary property file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".prp") as prop_file:
            prop_file.write(content)
            prop_file.flush()
            
            # Set the property file path on the wrapper
            self.wrapper.prop_file = prop_file.name
            
            # Call parse_property_file
            try:
                self.wrapper.parse_property_file()
                # Collect the parsed results
                results = []
                if self.wrapper.entry:
                    results.append(f'ENTRY={self.wrapper.entry}')
                if self.wrapper.prop:
                    results.append(f'PROP="{self.wrapper.prop}"')
                if self.wrapper.label:
                    results.append(f'LABEL="{self.wrapper.label}"')
                if self.wrapper.fail_function:
                    results.append(f'FAIL_FUNCTION="{self.wrapper.fail_function}"')
                output = '\n'.join(results)
            except SystemExit:
                # Handle cases where parse_property_file exits
                output = ""
            finally:
                os.unlink(prop_file.name)
                # Reset wrapper state for next test
                self.wrapper.prop = None
                self.wrapper.entry = None
                self.wrapper.label = None
                self.wrapper.fail_function = None
                
            return output

    def test_label_property(self):
        content = "CHECK( init(main()), LTL(G ! label(ERROR)) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="label"', output)
        self.assertIn('LABEL="ERROR"', output)

    def test_unreach_call_with_function(self):
        content = "CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="unreach_call"', output)
        self.assertIn('FAIL_FUNCTION="__VERIFIER_error"', output)

    def test_unreach_call_assert(self):
        content = "CHECK( init(main()), LTL(G assert) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="unreach_call"', output)

    def test_memsafety_valid_free(self):
        content = "CHECK( init(main()), LTL(G valid-free) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="memsafety"', output)

    def test_memsafety_valid_deref(self):
        content = "CHECK( init(main()), LTL(G valid-deref) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="memsafety"', output)

    def test_memsafety_valid_memtrack(self):
        content = "CHECK( init(main()), LTL(G valid-memtrack) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="memsafety"', output)

    def test_memcleanup(self):
        content = "CHECK( init(main()), LTL(G valid-memcleanup) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="memcleanup"', output)

    def test_overflow(self):
        content = "CHECK( init(main()), LTL(G ! overflow) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="overflow"', output)

    def test_termination(self):
        content = "CHECK( init(main()), LTL(F end) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="termination"', output)

    def test_runtime_exception(self):
        content = "CHECK( init(main()), LTL(G ! uncaught(java.lang.ArithmeticException)) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="runtime-exception"', output)
        self.assertIn('LABEL="java.lang.ArithmeticException"', output)

    def test_whitespace_handling(self):
        content = "  CHECK ( init ( main ( ) ) , LTL ( G ! label ( ERROR ) ) )  "
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=main', output)
        self.assertIn('PROP="label"', output)
        self.assertIn('LABEL="ERROR"', output)

    def test_different_entry_function(self):
        content = "CHECK( init(custom_main()), LTL(G assert) )"
        output = self.run_parse_property_file(content)
        self.assertIn('ENTRY=custom_main', output)
        self.assertIn('PROP="unreach_call"', output)

    def test_invalid_property(self):
        content = "CHECK( init(main()), LTL(G unknown_property) )"
        output = self.run_parse_property_file(content)
        # When property is not recognized, parse_property_file exits before setting anything
        self.assertEqual(output, "")

    def test_malformed_input(self):
        content = "This is not a valid property specification"
        output = self.run_parse_property_file(content)
        self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()