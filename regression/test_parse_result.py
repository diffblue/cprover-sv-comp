#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cbmc_wrapper import CBMCWrapper


class TestParseResult(unittest.TestCase):
    """Test cases for ToolWrapper.parse_result method"""
    
    def setUp(self):
        """Set up test instance"""
        self.wrapper = CBMCWrapper()
    
    def test_unmodelled_library_functions(self):
        """Test UNKNOWN result for unmodelled library functions"""
        log_content = """
Some output here
Unmodelled library functions have been called
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "UNKNOWN")
    
    def test_memory_leak_memcleanup_property(self):
        """Test memory leak detection with memcleanup property"""
        self.wrapper.prop = "memcleanup"
        log_content = """
Some output here
[main.1] __CPROVER_memory_leak == NULL
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-memcleanup)")
        
        # Test with alternative pattern (since [[:space:]] doesn't work in Python re)
        log_content = """
Some output here
[test.1] something __CPROVER_memory_leak == NULL
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-memcleanup)")
    
    def test_memory_leak_other_property(self):
        """Test memory leak detection with non-memcleanup property"""
        self.wrapper.prop = "memsafety"
        log_content = """
Some output here
[main.1] __CPROVER_memory_leak == NULL
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-memtrack)")
    
    def test_dynamically_allocated_memory_never_freed_memcleanup(self):
        """Test dynamically allocated memory never freed with memcleanup"""
        self.wrapper.prop = "memcleanup"
        log_content = """
Some output here
[main.1] dynamically allocated memory never freed in function
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-memcleanup)")
        
        # Test without brackets
        log_content = """
Some output here
  dynamically allocated memory never freed in main
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-memcleanup)")
    
    def test_dynamically_allocated_memory_never_freed_other(self):
        """Test dynamically allocated memory never freed with other property"""
        self.wrapper.prop = "memsafety"
        log_content = """
Some output here
[main.1] dynamically allocated memory never freed in function
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-memtrack)")
    
    def test_dereference_failure(self):
        """Test dereference failure detection"""
        log_content = """
Some output here
[main.1] dereference failure: pointer NULL
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
        
        # Test without brackets
        log_content = """
Some output here
  dereference failure: invalid pointer
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_array_bounds_lower(self):
        """Test array lower bound violation"""
        log_content = """
Some output here
[main.1] array index lower bound in arr[i]
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_array_bounds_upper(self):
        """Test array upper bound violation"""
        log_content = """
Some output here
  array index upper bound in buffer[10]
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_memcpy_source_region(self):
        """Test memcpy source region readable check"""
        log_content = """
Some output here
  memcpy source region readable
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_memset_destination_region(self):
        """Test memset destination region writeable check"""
        log_content = """
Some output here
  memset destination region writeable
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_double_free(self):
        """Test double free detection"""
        log_content = """
Some output here
[main.1] double free
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
        
        # Test at end of line
        log_content = """
Some output here
  double free
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
        
        # Test free argument must be NULL or valid pointer
        log_content = """
Some output here
  free argument must be NULL or valid pointer
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
    
    def test_free_stack_allocated(self):
        """Test free called for stack-allocated object"""
        log_content = """
Some output here
[main.1] free called for stack-allocated object
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
        
        # Test at end of line
        log_content = """
Some output here
  free called for stack-allocated object
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
    
    def test_free_argument_offset_zero_with_invalid(self):
        """Test free argument has offset zero with INVALID pointer"""
        log_content = """
Some output here
[main.1] free argument has offset zero
More output
  ptr=INVALID-HEAP
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_free_argument_offset_zero_without_invalid(self):
        """Test free argument has offset zero without INVALID pointer"""
        log_content = """
Some output here
  free argument has offset zero
More output
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
    
    def test_free_argument_dynamic_object_with_invalid(self):
        """Test free argument is dynamic object with INVALID pointer"""
        log_content = """
Some output here
[main.1] free argument is dynamic object
More output
  var=INVALID-123
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
        
        # Test with "must be"
        log_content = """
Some output here
  free argument must be dynamic object
More output
  variable=INVALID-PTR
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-deref)")
    
    def test_free_argument_dynamic_object_without_invalid(self):
        """Test free argument is dynamic object without INVALID pointer"""
        log_content = """
Some output here
[main.1] free argument is dynamic object
More output
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(valid-free)")
    
    def test_arithmetic_overflow(self):
        """Test arithmetic overflow on signed"""
        log_content = """
Some output here
[main.1] arithmetic overflow on signed
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(no-overflow)")
        
        # Test without brackets
        log_content = """
Some output here
  arithmetic overflow on signed addition
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(no-overflow)")
    
    def test_termination_property(self):
        """Test termination property handling"""
        self.wrapper.prop = "termination"
        log_content = """
Some output here
No specific pattern matched
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(termination)")
    
    def test_default_false_result(self):
        """Test default FALSE result when no pattern matches"""
        self.wrapper.prop = "unreach_call"
        log_content = """
Some output here
No specific pattern matched
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE")
    
    def test_tail_lines_extraction(self):
        """Test that only last 50 lines are considered"""
        # Create log with more than 50 lines
        lines = [f"Line {i}" for i in range(100)]
        lines.append("arithmetic overflow on signed")
        log_content = '\n'.join(lines)
        
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "FALSE(no-overflow)")
        
        # Move the pattern before the last 50 lines
        lines = [f"Line {i}" for i in range(10)]
        lines.append("arithmetic overflow on signed")
        lines.extend([f"Line {i}" for i in range(100)])
        log_content = '\n'.join(lines)
        
        result = self.wrapper.parse_result(log_content)
        # Should not match since it's not in the last 50 lines
        self.assertEqual(result, "FALSE")
    
    def test_priority_order(self):
        """Test that patterns are checked in the correct priority order"""
        # Unmodelled library functions should take precedence
        log_content = """
Some output here
Unmodelled library functions have been called
[main.1] double free
Final line
"""
        result = self.wrapper.parse_result(log_content)
        self.assertEqual(result, "UNKNOWN")


if __name__ == '__main__':
    unittest.main()