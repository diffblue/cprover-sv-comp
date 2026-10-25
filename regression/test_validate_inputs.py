#!/usr/bin/env python3
"""Regression tests for validate_inputs functionality"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Import the wrapper - handle different import scenarios
try:
    from cbmc_wrapper import CBMCWrapper
except ImportError:
    # Import tool_wrapper as the base class
    from tool_wrapper import ToolWrapper
    from cbmc_wrapper import CBMCWrapper
    
    # Ensure CBMCWrapper inherits from ToolWrapper
    CBMCWrapper.__bases__ = (ToolWrapper,)


class TestValidateInputs(unittest.TestCase):
    """Test cases for validate_inputs method via main entry point"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.c")
        self.prop_file = os.path.join(self.temp_dir, "test.prp")
        
        # Create test files
        with open(self.test_file, 'w') as f:
            f.write("int main() { return 0; }\n")
            
        with open(self.prop_file, 'w') as f:
            f.write("CHECK( init(main()), LTL(G assert) )\n")
            
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_missing_benchmark_file(self):
        """Test that validate_inputs fails when no benchmark files provided"""
        with self.assertRaises(SystemExit) as cm:
            sys.argv = ['cbmc_wrapper.py', '--propertyfile', self.prop_file]
            wrapper = CBMCWrapper()
            wrapper.parse_arguments(['--propertyfile', self.prop_file])
            wrapper.validate_inputs()
            
        self.assertEqual(cm.exception.code, 1)
        
    def test_missing_property_file(self):
        """Test that validate_inputs fails when no property file provided"""
        with self.assertRaises(SystemExit) as cm:
            sys.argv = ['cbmc_wrapper.py', self.test_file]
            wrapper = CBMCWrapper()
            wrapper.parse_arguments([self.test_file])
            wrapper.validate_inputs()
            
        self.assertEqual(cm.exception.code, 1)
        
    def test_nonexistent_benchmark_file(self):
        """Test that validate_inputs fails when benchmark file doesn't exist"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.c")
        
        with self.assertRaises(SystemExit) as cm:
            sys.argv = ['cbmc_wrapper.py', nonexistent_file, '--propertyfile', self.prop_file]
            wrapper = CBMCWrapper()
            wrapper.parse_arguments([nonexistent_file, '--propertyfile', self.prop_file])
            wrapper.validate_inputs()
            
        self.assertEqual(cm.exception.code, 1)
        
    def test_nonexistent_property_file(self):
        """Test that validate_inputs fails when property file doesn't exist"""
        nonexistent_prop = os.path.join(self.temp_dir, "nonexistent.prp")
        
        with self.assertRaises(SystemExit) as cm:
            sys.argv = ['cbmc_wrapper.py', self.test_file, '--propertyfile', nonexistent_prop]
            wrapper = CBMCWrapper()
            wrapper.parse_arguments([self.test_file, '--propertyfile', nonexistent_prop])
            wrapper.validate_inputs()
            
        self.assertEqual(cm.exception.code, 1)
        
    def test_valid_inputs(self):
        """Test that validate_inputs succeeds with valid inputs"""
        # This should not raise SystemExit
        sys.argv = ['cbmc_wrapper.py', self.test_file, '--propertyfile', self.prop_file]
        wrapper = CBMCWrapper()
        wrapper.parse_arguments([self.test_file, '--propertyfile', self.prop_file])
        
        # Should not raise exception
        wrapper.validate_inputs()
        
        # Verify internal state
        self.assertEqual(wrapper.benchmarks, [self.test_file])
        self.assertEqual(wrapper.prop_file, self.prop_file)
        
    def test_multiple_benchmark_files(self):
        """Test validate_inputs with multiple benchmark files"""
        test_file2 = os.path.join(self.temp_dir, "test2.c")
        with open(test_file2, 'w') as f:
            f.write("void foo() {}\n")
            
        wrapper = CBMCWrapper()
        wrapper.parse_arguments([self.test_file, test_file2, '--propertyfile', self.prop_file])
        
        # Should validate using first benchmark file
        wrapper.validate_inputs()
        
        self.assertEqual(len(wrapper.benchmarks), 2)
        
    def test_empty_benchmark_file(self):
        """Test behavior with empty benchmark file"""
        empty_file = os.path.join(self.temp_dir, "empty.c")
        open(empty_file, 'w').close()  # Create empty file
        
        # Should not fail validation - file exists
        wrapper = CBMCWrapper()
        wrapper.parse_arguments([empty_file, '--propertyfile', self.prop_file])
        wrapper.validate_inputs()

if __name__ == '__main__':
    unittest.main()