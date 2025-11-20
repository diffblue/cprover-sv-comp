#!/usr/bin/env python3

import unittest
import sys
import os
import tempfile
import hashlib
from datetime import datetime
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cbmc_wrapper import CBMCWrapper


class TestProcessGraphML(unittest.TestCase):
    """Test cases for ToolWrapper.process_graphml method"""
    
    def setUp(self):
        """Set up test instance"""
        self.wrapper = CBMCWrapper()
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        self.wrapper.log_file = self.log_file
        
        # Create test benchmark file
        self.benchmark_file = os.path.join(self.temp_dir, "test.c")
        with open(self.benchmark_file, 'w') as f:
            f.write("int main() { return 0; }")
        self.wrapper.benchmarks = [self.benchmark_file]
        
        # Create test property file
        self.prop_file = os.path.join(self.temp_dir, "test.prp")
        with open(self.prop_file, 'w') as f:
            f.write("CHECK(init(main()), LTL(G !call(reach_error())))")
        self.wrapper.prop_file = self.prop_file
        
        # Set tool name
        self.wrapper.tool_name = "CBMC"
        self.wrapper.bit_width = "64"
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_missing_witness_file(self):
        """Test when witness file doesn't exist"""
        # Don't create the witness file
        result = self.wrapper.process_graphml(0)
        self.assertIsNone(result)
    
    def test_correctness_witness(self):
        """Test correctness witness generation (exit_code = 0)"""
        # Create a sample witness file
        witness_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph edgedefault="directed">
    <node id="N0">
      <data key="entry">true</data>
    </node>
  </graph>
</graphml>"""
        
        witness_path = f"{self.log_file}.witness"
        with open(witness_path, 'w') as f:
            f.write(witness_content)
        
        # Mock datetime to have consistent timestamp
        with patch('tool_wrapper.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            result = self.wrapper.process_graphml(0)
        
        self.assertIsNotNone(result)
        self.assertIn('<data key="witness-type">correctness_witness</data>', result)
        self.assertIn('<data key="producer">CBMC</data>', result)
        self.assertIn('<data key="architecture">64bit</data>', result)
        self.assertIn('<data key="creationtime">2024-01-01T12:00:00</data>', result)
        
        # Check program hash
        with open(self.benchmark_file, 'rb') as f:
            expected_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertIn(f'<data key="programhash">{expected_hash}</data>', result)
        
        # Check specification
        self.assertIn('<data key="specification">CHECK(init(main()), LTL(G !call(reach_error())))</data>', result)
        
        # Check programfile
        self.assertIn(f'<data key="programfile">{self.benchmark_file}</data>', result)
    
    def test_violation_witness(self):
        """Test violation witness generation (exit_code = 10)"""
        # Create a sample witness file
        witness_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph edgedefault="directed">
    <node id="N0">
      <data key="entry">true</data>
    </node>
    <edge source="N0" target="N1">
      <data key="violation">true</data>
    </edge>
  </graph>
</graphml>"""
        
        witness_path = f"{self.log_file}.witness"
        with open(witness_path, 'w') as f:
            f.write(witness_content)
        
        # Mock datetime to have consistent timestamp
        with patch('tool_wrapper.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            result = self.wrapper.process_graphml(10)
        
        self.assertIsNotNone(result)
        self.assertIn('<data key="witness-type">violation_witness</data>', result)
        self.assertIn('<data key="producer">CBMC</data>', result)
        self.assertIn('<data key="architecture">64bit</data>', result)
        self.assertIn('<data key="creationtime">2024-01-01T12:00:00</data>', result)
    
    def test_metadata_insertion_position(self):
        """Test that metadata is inserted after <graph edgedefault="directed">"""
        witness_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key attr.name="entry" attr.type="boolean" for="node" id="entry"/>
  <graph edgedefault="directed">
    <node id="N0">
      <data key="entry">true</data>
    </node>
  </graph>
</graphml>"""
        
        witness_path = f"{self.log_file}.witness"
        with open(witness_path, 'w') as f:
            f.write(witness_content)
        
        result = self.wrapper.process_graphml(0)
        
        # Check that metadata appears right after <graph edgedefault="directed">
        graph_tag_pos = result.find('<graph edgedefault="directed">')
        self.assertNotEqual(graph_tag_pos, -1)
        
        # Find the position right after the graph tag
        after_graph_tag = graph_tag_pos + len('<graph edgedefault="directed">')
        
        # Check that witness-type appears shortly after
        witness_type_pos = result.find('<data key="witness-type">')
        self.assertNotEqual(witness_type_pos, -1)
        self.assertLess(witness_type_pos, after_graph_tag + 100)  # Should be very close
        
        # Ensure original structure is preserved
        self.assertIn('<node id="N0">', result)
        self.assertIn('<data key="entry">true</data>', result)
    
    def test_different_architectures(self):
        """Test witness generation with different architectures"""
        witness_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph edgedefault="directed">
  </graph>
</graphml>"""
        
        witness_path = f"{self.log_file}.witness"
        with open(witness_path, 'w') as f:
            f.write(witness_content)
        
        # Test with 32-bit architecture
        self.wrapper.bit_width = "32"
        result = self.wrapper.process_graphml(0)
        self.assertIn('<data key="architecture">32bit</data>', result)
        
        # Test with 64-bit architecture
        self.wrapper.bit_width = "64"
        result = self.wrapper.process_graphml(0)
        self.assertIn('<data key="architecture">64bit</data>', result)
    
    def test_special_characters_in_specification(self):
        """Test handling of special XML characters in specification"""
        # Create property file with special characters
        with open(self.prop_file, 'w') as f:
            f.write('CHECK(init(main()), LTL(G !call(error()) & F x > 5))')
        
        witness_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph edgedefault="directed">
  </graph>
</graphml>"""
        
        witness_path = f"{self.log_file}.witness"
        with open(witness_path, 'w') as f:
            f.write(witness_content)
        
        result = self.wrapper.process_graphml(0)
        self.assertIsNotNone(result)
        # The & and > characters should be preserved or properly encoded
        self.assertIn('CHECK(init(main()), LTL(G !call(error()) & F x > 5))', result)
    
    def test_empty_witness_file(self):
        """Test handling of empty witness file"""
        witness_path = f"{self.log_file}.witness"
        with open(witness_path, 'w') as f:
            f.write("")
        
        # Should handle empty file gracefully
        result = self.wrapper.process_graphml(0)
        # Result will depend on how regex handles empty string
        # but it should not crash
        self.assertIsNotNone(result)  # Will contain the empty string with metadata added


if __name__ == '__main__':
    unittest.main()