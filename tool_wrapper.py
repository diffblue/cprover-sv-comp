import os
import sys
import re
import json
import uuid
import tempfile
import subprocess
import hashlib
from datetime import datetime, timezone
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

# Calls of functions returning nondeterministic values, whose results are given
# by function_return waypoints in YAML witnesses
NONDET_CALL_PATTERNS = {
    "C": re.compile(r"\b__VERIFIER_nondet_\w+\s*\("),
    "Java": re.compile(r"\bnondet\w*\s*\("),
}


def yaml_string(s):
    """Return s as a double-quoted YAML scalar (JSON strings are valid YAML)"""
    return json.dumps(s)


def find_input_file(file_name, input_files):
    """Return the input file that a location's file name refers to.

    The tools give the file names as passed to the front end, e.g. relative to
    the working directory for C or relative to the class path for Java, so the
    trailing path components are matched."""
    name = os.path.normpath(file_name)
    for input_file in input_files:
        if os.path.normpath(input_file) == name:
            return input_file
    name_parts = name.split(os.sep)
    for input_file in input_files:
        input_parts = os.path.normpath(input_file).split(os.sep)
        if input_parts[-len(name_parts):] == name_parts:
            return input_file
    return None


def nondet_call_columns(line, language):
    """Return the columns (starting at 1) that function_return waypoints for
    the nondet calls on the given source line point to: the closing
    parenthesis of the call for C, the opening parenthesis for Java"""
    columns = []
    for match in NONDET_CALL_PATTERNS[language].finditer(line):
        open_paren = match.end() - 1
        if language == "Java":
            columns.append(open_paren + 1)
            continue
        depth = 0
        for pos in range(open_paren, len(line)):
            if line[pos] == "(":
                depth += 1
            elif line[pos] == ")":
                depth -= 1
                if depth == 0:
                    columns.append(pos + 1)
                    break
    return columns


def call_start_column(line, function):
    """Return the column (starting at 1) of the first call of function on the
    given source line, or None"""
    match = re.search(r"\b" + re.escape(function) + r"\s*\(", line)
    return match.start() + 1 if match else None


def violated_specification(prop_file_content, result):
    """Return the property of the property file that the result says is
    violated, e.g. "CHECK( init(main()), LTL(G valid-deref) )" for
    "FALSE(valid-deref)" and a memory-safety property file"""
    checks = [l.strip() for l in prop_file_content.splitlines() if l.strip()]
    match = re.match(r"^FALSE\((\S+)\)$", result or "")
    if match and len(checks) > 1:
        for check in checks:
            if match.group(1) in check:
                return check
    return "\n".join(checks)


def complete_yaml_witness(witness, input_files, specification, fail_function):
    """Complete a violation witness as produced by CBMC or JBMC with the
    metadata of the verification task and the columns of the locations.

    The tools emit locations with the file name as given to the front end and
    without columns. Each location is mapped to an input file;
    function_return waypoints that cannot be mapped are dropped. The k-th of
    consecutive function_return waypoints on the same line gets the column of
    the k-th nondet call on that line."""
    language_match = re.search(r'^      language: "(\w+)"$', witness, re.MULTILINE)
    language = language_match.group(1) if language_match else "C"

    header, separator, content = witness.partition("\n  content:")
    blocks = re.split(r"(?m)^(?=  - segment:$)", content)
    content_head, waypoint_blocks = blocks[0], blocks[1:]

    task = ["      input_files:"]
    task += [f"      - {yaml_string(f)}" for f in input_files]
    task.append("      input_file_hashes:")
    for f in input_files:
        with open(f, "rb") as file:
            digest = hashlib.sha256(file.read()).hexdigest()
        task.append(f"        {yaml_string(f)}: {yaml_string(digest)}")
    task.append(f"      specification: {yaml_string(specification)}")
    header = header.replace("\n    task:", "\n    task:\n" + "\n".join(task), 1)

    lines_of = {}
    def source_line(file_name, line):
        if file_name not in lines_of:
            with open(file_name, errors="replace") as file:
                lines_of[file_name] = file.read().splitlines()
        lines = lines_of[file_name]
        return lines[line - 1] if 0 < line <= len(lines) else ""

    completed = []
    previous = None  # (file, line) of the previous function_return waypoint
    occurrence = 0
    for block in waypoint_blocks:
        waypoint_type = re.search(r'^        type: "(\w+)"$', block, re.MULTILINE).group(1)
        file_match = re.search(r'^          file_name: (".*")$', block, re.MULTILINE)
        line = int(re.search(r"^          line: (\d+)$", block, re.MULTILINE).group(1))
        input_file = find_input_file(json.loads(file_match.group(1)), input_files)
        if input_file is None:
            if waypoint_type == "function_return":
                continue
            completed.append(block)
            continue

        column = None
        if waypoint_type == "function_return":
            occurrence = occurrence + 1 if previous == (input_file, line) else 0
            previous = (input_file, line)
            columns = nondet_call_columns(source_line(input_file, line), language)
            if len(columns) == 1:
                column = columns[0]
            elif occurrence < len(columns):
                column = columns[occurrence]
        elif waypoint_type == "target" and fail_function:
            column = call_start_column(source_line(input_file, line), fail_function)

        block = block.replace(
            file_match.group(0), f"          file_name: {yaml_string(input_file)}", 1)
        if column is not None:
            block = re.sub(
                r"(?m)^(          line: \d+)$", rf"\1\n          column: {column}", block, count=1)
        completed.append(block)

    if not waypoint_blocks:
        return header + separator + content
    if not completed:
        return header + separator + " []\n"
    return header + separator + content_head + "".join(completed)


def make_yaml_witness(producer, version, language, waypoints,
                      entry_type="violation_sequence", data_model=None):
    """Return a witness in the format produced by CBMC and JBMC, i.e.,
    without the input files and the specification.

    Each waypoint is a dict with the keys type, file_name, line and, for
    function_return waypoints, value. A correctness witness (entry_type
    invariant_set) without waypoints contains no invariants."""
    formats = {"C": "acsl_expression", "Java": "ext_java_expression"}
    out = [
        f"- entry_type: {yaml_string(entry_type)}",
        "  metadata:",
        f"    format_version: {yaml_string('2.4' if language == 'Java' else '2.0')}",
        f"    uuid: {yaml_string(str(uuid.uuid4()))}",
        "    creation_time: "
        + yaml_string(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
        "    producer:",
        f"      name: {yaml_string(producer)}",
        f"      version: {yaml_string(version)}",
        "    task:",
    ]
    if data_model:
        out.append(f"      data_model: {yaml_string(data_model)}")
    out += [
        f"      language: {yaml_string(language)}",
        "  content:" + ("" if waypoints else " []"),
    ]
    for waypoint in waypoints:
        out += [
            "  - segment:",
            "    - waypoint:",
            f"        type: {yaml_string(waypoint['type'])}",
            '        action: "follow"',
        ]
        if "value" in waypoint:
            out += [
                "        constraint:",
                "          value: " + yaml_string("\\result == " + waypoint["value"]),
                f"          format: {yaml_string(formats[language])}",
            ]
        out += [
            "        location:",
            f"          file_name: {yaml_string(waypoint['file_name'])}",
            f"          line: {waypoint['line']}",
        ]
    return "\n".join(out) + "\n"


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
        self.witness_format = None
        self.input_files = []
        self.language = "C"
        self.prop = None
        self.entry = None
        self.label = None
        self.fail_function = None
        self.property_options = ""
        self.log_file = None
        self.bm_dir = None
        
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
                self.witness_format = "graphml"
                i += 1
            elif args[i] == "--witness" and i + 1 < len(args):
                self.witness_file = args[i + 1]
                self.witness_format = "yaml"
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
            
        # A property file may contain several properties, one per line, as for
        # memory safety; they all map to the same tool options.
        lines = [line for line in content.splitlines() if line.strip()]
        content = lines[0] if lines else ""

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
        elif re.search(r"(\[.*\] .*__CPROVER_memory_leak == NULL|\s*__CPROVER_memory_leak == NULL$)", tail_content, re.MULTILINE):
            if self.prop == "memcleanup":
                return "FALSE(valid-memcleanup)"
            else:
                return "FALSE(valid-memtrack)"
        elif re.search(r"(\[.*\] |\s*)dynamically allocated memory never freed in", tail_content):
            if self.prop == "memcleanup":
                return "FALSE(valid-memcleanup)"
            else:
                return "FALSE(valid-memtrack)"
        elif re.search(r"(\[.*\] |\s*)dereference failure:", tail_content):
            return "FALSE(valid-deref)"
        elif re.search(r"(\[.*\] |\s*)array.* (lower|upper) bound in", tail_content):
            return "FALSE(valid-deref)"
        elif re.search(r"\s+mem(cpy|set|move) (source region readable|destination region writeable)", tail_content):
            return "FALSE(valid-deref)"
        elif re.search(r"(\[.*\] double free|\s*double free$|\s*free argument must be NULL or valid pointer$)", tail_content, re.MULTILINE):
            return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] free called for stack-allocated object|\s*free called for stack-allocated object$)", tail_content, re.MULTILINE):
            return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] free argument has offset zero|\s*free argument has offset zero$)", tail_content, re.MULTILINE):
            if re.search(r"\s+[a-zA-Z0-9_]+=INVALID-", tail_content):
                return "FALSE(valid-deref)"
            else:
                return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] |\s*)free argument (is|must be) dynamic object", tail_content):
            if re.search(r"\s+[a-zA-Z0-9_]+=INVALID-", tail_content):
                return "FALSE(valid-deref)"
            else:
                return "FALSE(valid-free)"
        elif re.search(r"(\[.*\] |\s*)arithmetic overflow on signed", tail_content):
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
        
    def witness_options(self):
        """Return the tool options for writing the witness to the log file"""
        option = "--witness" if self.witness_format == "yaml" else "--graphml-witness"
        return [option, f"{self.log_file}.witness"]

    def tool_version(self):
        """Return the version of the tool"""
        return subprocess.run(
            [self.tool_binary, "--version"], capture_output=True, text=True).stdout.strip()

    def process_yaml(self, exit_code, result):
        """Complete the YAML witness written by the tool"""
        if exit_code == 0:
            # a correctness witness without invariants
            witness_content = make_yaml_witness(
                self.tool_name, self.tool_version(), self.language, [],
                entry_type="invariant_set",
                data_model=None if self.language == "Java" else
                ("ILP32" if self.bit_width == "32" else "LP64"))
        else:
            witness_path = f"{self.log_file}.witness"
            if not os.path.exists(witness_path):
                return None
            with open(witness_path, 'r') as f:
                witness_content = f.read()
        with open(self.prop_file, 'r') as f:
            specification = violated_specification(f.read(), result)

        return complete_yaml_witness(
            witness_content, self.input_files, specification, self.fail_function)

    def process_witness(self, exit_code, result=None):
        """Process the witness written by the tool"""
        if self.witness_format == "yaml":
            return self.process_yaml(exit_code, result)
        return self.process_graphml(exit_code)

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
            # the tools may replace benchmark files by patched copies
            self.input_files = list(self.benchmarks)
            
            # Run the tool
            ec = self.run()
            
            # Process results
            log_ok_path = f"{self.log_file}.ok"
            if not os.path.exists(log_ok_path) or os.path.getsize(log_ok_path) == 0:
                sys.exit(1)
                
            with open(log_ok_path, 'r') as f:
                log_content = f.read()
                
            print(log_content)
                
            # Generate result
            if ec == 0:
                if self.witness_file:
                    witness_content = self.process_witness(ec)
                    if witness_content:
                        with open(self.witness_file, 'w') as f:
                            f.write(witness_content)
                print("TRUE")
            elif ec == 10:
                result = self.parse_result(log_content)
                if self.witness_file:
                    witness_content = self.process_witness(ec, result)
                    if witness_content:
                        with open(self.witness_file, 'w') as f:
                            f.write(witness_content)
                print(result)
            else:
                print("UNKNOWN")
                
            sys.exit(ec)
            
        finally:
            self.cleanup()