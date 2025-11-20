import os
import sys
import re
import tempfile
import subprocess
import hashlib
from datetime import datetime
from abc import ABC, abstractmethod
import glob
import signal
import shutil

# Property options mapping
PROPERTY_OPTIONS = {
    "label": "--error-label",
    "unreach_call": "",
    "termination": "",
    "overflow": "--signed-overflow-check --no-assertions",
    "memsafety": "--pointer-check --memory-leak-check --bounds-check --no-assertions",
    "memcleanup": "--pointer-check --memory-leak-check --memory-cleanup-check --bounds-check --no-assertions",
    "runtime-exception": "--uncaught-exception-check-only-for"
}

class ToolWrapper(ABC):
    """Abstract base class for tool wrappers"""
    
    def __init__(self):
        self.tool_binary = None
        self.tool_name = None
        self.find_options = ""
        self.bit_width = "64"
        self.obj_bits = "11"
        self.benchmarks = []
        self.prop_file = ""
        self.witness_file = ""
        self.prop = None
        self.entry = None
        self.label = None
        self.fail_function = None
        self.property_options = ""
        self.log_file = None
        self.bm_dir = None
        self.ec = None
        
    def parse_arguments(self, args):
        """Parse command line arguments"""
        i = 0
        while i < len(args):
            if args[i] == "--32":
                self.bit_width = "32"
            elif args[i] == "--64":
                self.bit_width = "64"
            elif args[i] == "--propertyfile" and i + 1 < len(args):
                self.prop_file = args[i + 1]
                i += 1
            elif args[i] == "--graphml-witness" and i + 1 < len(args):
                self.witness_file = args[i + 1]
                i += 1
            elif args[i] == "--version":
                self.print_version()
                sys.exit(0)
            else:
                # Find source files based on find_options
                if self.find_options:
                    # Parse find_options to extract pattern
                    pattern_match = re.search(r"-name\s+'([^']+)'", self.find_options)
                    if pattern_match:
                        pattern = pattern_match.group(1)
                        found_files = glob.glob(os.path.join(args[i], "**", pattern), recursive=True)
                        self.benchmarks.extend(found_files)
                else:
                    self.benchmarks.append(args[i])
            i += 1
            
    def validate_inputs(self):
        """Validate required inputs"""
        if not self.benchmarks or not self.prop_file:
            print("Missing benchmark or property file")
            sys.exit(1)
            
        if not os.path.exists(self.benchmarks[0]) or not os.path.exists(self.prop_file):
            print("Empty benchmark or property file")
            sys.exit(1)
            
    def parse_property_file(self):
        """Parse the property file to extract property type and parameters"""
        with open(self.prop_file, 'r') as f:
            content = f.read()
            
        # Remove whitespace
        content = re.sub(r'\s+', '', content)
        
        # Match the CHECK pattern
        match = re.match(r'^CHECK\(init\((\S+)\(\)\),LTL\((\S+)\)\)$', content)
        if match:
            self.entry = match.group(1)
            ltl_formula = match.group(2)
            
            # Parse different property types
            if re.match(r'^G!label\((\S+)\)$', ltl_formula):
                self.prop = "label"
                self.label = re.match(r'^G!label\((\S+)\)$', ltl_formula).group(1)
            elif re.match(r'^G!call\((?P<fn>\S+)\(\)\)$', ltl_formula):
                self.prop = "unreach_call"
                self.fail_function = re.match(r'^G!call\((?P<fn>\S+)\(\)\)$', ltl_formula).group('fn')
            elif ltl_formula == "Gassert":
                self.prop = "unreach_call"
            elif re.match(r'^Gvalid-(free|deref|memtrack)$', ltl_formula):
                self.prop = "memsafety"
            elif ltl_formula == "Gvalid-memcleanup":
                self.prop = "memcleanup"
            elif ltl_formula == "G!overflow":
                self.prop = "overflow"
            elif ltl_formula == "Fend":
                self.prop = "termination"
            elif re.match(r'^G!uncaught\((\S+)\)$', ltl_formula):
                self.prop = "runtime-exception"
                self.label = re.match(r'^G!uncaught\((\S+)\)$', ltl_formula).group(1)
                
        if not self.prop:
            print("Unrecognized property specification")
            sys.exit(1)
            
        # Set property options
        if self.prop == "label":
            self.property_options = f"{PROPERTY_OPTIONS[self.prop]} {self.label}"
        elif self.prop == "runtime-exception":
            self.property_options = f"{PROPERTY_OPTIONS[self.prop]} {self.label}"
        else:
            self.property_options = PROPERTY_OPTIONS.get(self.prop, "")
            
    def parse_result(self, log_content):
        """Parse the tool output to determine the result"""
        lines = log_content.split('\n')
        tail_lines = lines[-50:] if len(lines) >= 50 else lines
        tail_content = '\n'.join(tail_lines)
        
        if re.search(r"Unmodelled library functions have been called", tail_content):
            return "UNKNOWN"
        elif re.search(r"(\[.*\] .*__CPROVER_memory_leak == NULL|[[:space:]]*__CPROVER_memory_leak == NULL$)", tail_content):
            if self.prop == "memcleanup":
                return "FALSE(valid-memcleanup)"
            else:
                return "FALSE(valid-memtrack)"
        elif re.search(r"(\[.*\] |[[:space:]]*)dynamically allocated memory never freed in", tail_content):
            if self.prop == "memcleanup":
                return "FALSE(valid-memcleanup)"
            else:
                return "FALSE(valid-memtrack)"
        elif re.search(r"(\[.*\] |[[:space:]]*)dereference failure:", tail_content):
            return "FALSE(valid-deref)"
        elif re.search(r"(\[.*\] |[[:space:]]*)array.* (lower|upper) bound in", tail_content):
            return "FALSE(valid-deref)"
        elif re.search(r"[[:space:]]+mem(cpy|set|move) (source region readable|destination region writeable)", tail_content):
            return "FALSE(valid-deref)"
        elif re.search(r"(\[.*\] double free|[[:space:]]*double free$|[[:space:]]*free argument must be NULL or valid pointer$)", tail_content):
            return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] free called for stack-allocated object|[[:space:]]*free called for stack-allocated object$)", tail_content):
            return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] free argument has offset zero|[[:space:]]* free argument has offset zero$)", tail_content):
            if re.search(r"[[:space:]]+[a-zA-Z0-9_]+=INVALID-", tail_content):
                return "FALSE(valid-deref)"
            else:
                return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] |[[:space:]]*)free argument (is|must be) dynamic object", tail_content):
            if re.search(r"[[:space:]]+[a-zA-Z0-9_]+=INVALID-", tail_content):
                return "FALSE(valid-deref)"
            else:
                return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] |[[:space:]]*)arithmetic overflow on signed", tail_content):
            return "FALSE(no-overflow)"
        elif self.prop == "termination":
            return "FALSE(termination)"
        else:
            return "FALSE"
            
    def process_graphml(self, exit_code):
        """Process and generate GraphML witness"""
        witness_path = f"{self.log_file}.witness"
        if not os.path.exists(witness_path):
            return None
            
        with open(witness_path, 'r') as f:
            witness_content = f.read()
            
        # Determine witness type
        witness_type = "correctness_witness" if exit_code == 0 else "violation_witness"
        
        # Calculate program hash
        with open(self.benchmarks[0], 'rb') as f:
            program_hash = hashlib.sha256(f.read()).hexdigest()
            
        # Read property specification
        with open(self.prop_file, 'r') as f:
            specification = f.read().strip()
            
        # Create metadata to insert
        metadata = f"""<data key="witness-type">{witness_type}</data>
      <data key="producer">{self.tool_name}</data>
      <data key="specification">{specification}</data>
      <data key="programfile">{self.benchmarks[0]}</data>
      <data key="programhash">{program_hash}</data>
      <data key="architecture">{self.bit_width}bit</data>
      <data key="creationtime">{datetime.now().isoformat()}</data>"""
      
        # Insert metadata after <graph edgedefault="directed">
        processed_witness = re.sub(
            r'(<graph edgedefault="directed">)',
            r'\1\n      ' + metadata,
            witness_content
        )
        
        return processed_witness
        
    def setup_environment(self):
        """Set up temporary directories and files"""
        # Create temporary directory for benchmarks
        self.bm_dir = tempfile.mkdtemp(prefix=f"{self.tool_name}-benchmark.")
        
        # Create temporary log file
        log_fd, self.log_file = tempfile.mkstemp(prefix=f"{self.tool_name}-log.")
        os.close(log_fd)
        
        # Set up GMON_OUT_PREFIX
        os.environ['GMON_OUT_PREFIX'] = f"{os.path.basename(self.benchmarks[0])}.gmon.out"
        
    def cleanup(self):
        """Clean up temporary files"""
        if self.log_file:
            for suffix in ['', '.latest', '.ok', '.witness', '.bin', '.ok1', '.ok2']:
                path = f"{self.log_file}{suffix}"
                if os.path.exists(path):
                    os.remove(path)
        if self.bm_dir and os.path.exists(self.bm_dir):
            shutil.rmtree(self.bm_dir)
            
    @abstractmethod
    def run(self):
        """Run the tool - to be implemented by subclasses"""
        pass
        
    @abstractmethod
    def print_version(self):
        """Print tool version - to be implemented by subclasses"""
        pass
        
    def execute(self):
        """Main execution method"""
        try:
            self.validate_inputs()
            self.parse_property_file()
            self.setup_environment()           
            # Export environment variables
            os.environ['ENTRY'] = self.entry
            os.environ['PROPERTY'] = self.property_options
            os.environ['BIT_WIDTH'] = self.bit_width
            os.environ['BM'] = ' '.join(self.benchmarks)
            os.environ['PROP'] = self.prop
            os.environ['OBJ_BITS'] = self.obj_bits
            
            # Run the tool
            self.run()
            
            # Process results
            log_ok_path = f"{self.log_file}.ok"
            if not os.path.exists(log_ok_path) or os.path.getsize(log_ok_path) == 0:
                sys.exit(1)
                
            with open(log_ok_path, 'r') as f:
                log_content = f.read()
                
            print(log_content)
            
            # Extract exit code from log
            ec_match = re.search(r'EC=(\d+)', log_content)
            if ec_match:
                self.ec = int(ec_match.group(1))
            else:
                self.ec = 42
                
            # Generate result
            if self.ec == 0:
                if self.witness_file:
                    witness_content = self.process_graphml(self.ec)
                    if witness_content:
                        with open(self.witness_file, 'w') as f:
                            f.write(witness_content)
                print("TRUE")
            elif self.ec == 10:
                if self.witness_file:
                    witness_content = self.process_graphml(self.ec)
                    if witness_content:
                        with open(self.witness_file, 'w') as f:
                            f.write(witness_content)
                result = self.parse_result(log_content)
                print(result)
            else:
                print("UNKNOWN")
                
            sys.exit(self.ec)
            
        finally:
            self.cleanup()