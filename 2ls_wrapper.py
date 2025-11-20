#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import signal
from tool_wrapper import ToolWrapper

class TwoLSWrapper(ToolWrapper):
    """2LS-specific wrapper implementation"""
    
    def __init__(self):
        super().__init__()
        self.tool_binary = "./2ls-binary"
        self.tool_name = "2LS"
        self.find_options = ""
        
    def print_version(self):
        """Print 2LS version"""
        subprocess.run([self.tool_binary, "--version"])
        
    def run(self):
        """Run 2LS"""
        # Compile with goto-cc
        gmon_suffix = os.environ.get('GMON_OUT_PREFIX', '')
        os.environ['GMON_OUT_PREFIX'] = f"goto-cc_{gmon_suffix}"
        
        goto_cc_cmd = ["./goto-cc", f"-m{self.bit_width}", "--function", self.entry] + self.benchmarks + ["-o", f"{self.log_file}.bin"]
        subprocess.run(goto_cc_cmd, check=True)
        
        # Handle fail function if specified
        if self.fail_function:
            goto_instrument_cmd = [
                "./goto-instrument", f"{self.log_file}.bin", f"{self.log_file}.bin",
                "--remove-function-body", self.fail_function,
                "--generate-function-body", self.fail_function,
                "--generate-function-body-options", "assert-false"
            ]
            subprocess.run(goto_instrument_cmd, check=True)
            
        os.environ['GMON_OUT_PREFIX'] = f"2ls_{gmon_suffix}"
        
        if self.prop == "termination":
            # Run termination and non-termination analysis in parallel
            return self._run_termination_analysis()
        else:
            # Run standard analysis
            property_options = self.property_options + " --heap --arrays --values-refine --k-induction --competition-mode"
            
            cmd = [
                self.tool_binary,
                "--graphml-witness", f"{self.log_file}.witness",
                "--object-bits", self.obj_bits
            ] + property_options.split() + [f"{self.log_file}.bin"]
            
            with open(f"{self.log_file}.ok", 'w') as log:
                result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
                ec = result.returncode
                
            return ec
                
    def _run_termination_analysis(self):
        """Run termination and non-termination analysis in parallel"""
        property1 = self.property_options + " --termination --competition-mode"
        property2 = self.property_options + " --nontermination --competition-mode"
        
        # Prepare commands
        cmd1 = [
            self.tool_binary,
            "--graphml-witness", f"{self.log_file}.witness",
            "--object-bits", self.obj_bits
        ] + property1.split() + [f"{self.log_file}.bin"]
        
        cmd2 = [
            self.tool_binary,
            "--graphml-witness", f"{self.log_file}.witness",
            "--object-bits", self.obj_bits
        ] + property2.split() + [f"{self.log_file}.bin"]
        
        # Start both processes
        log1 = open(f"{self.log_file}.ok1", 'w')
        log2 = open(f"{self.log_file}.ok2", 'w')
        
        proc1 = subprocess.Popen(cmd1, stdout=log1, stderr=subprocess.STDOUT)
        proc2 = subprocess.Popen(cmd2, stdout=log2, stderr=subprocess.STDOUT)
        
        # Wait for one to finish
        finished_proc = None
        other_proc = None
        ec = None
        
        while finished_proc is None:
            if proc1.poll() is not None:
                finished_proc = proc1
                other_proc = proc2
                ec = proc1.returncode
                log_to_use = f"{self.log_file}.ok1"
            elif proc2.poll() is not None:
                finished_proc = proc2
                other_proc = proc1
                ec = proc2.returncode
                log_to_use = f"{self.log_file}.ok2"
            else:
                time.sleep(0.1)
                
        log1.close()
        log2.close()
        
        # If the result is inconclusive, wait for the other
        if ec == 5:
            other_proc.wait()
            ec = other_proc.returncode
            if other_proc == proc1:
                log_to_use = f"{self.log_file}.ok1"
            else:
                log_to_use = f"{self.log_file}.ok2"
        else:
            # Kill the other process
            try:
                other_proc.kill()
                other_proc.wait()
            except:
                pass
                
        # Move the appropriate log file
        os.rename(log_to_use, f"{self.log_file}.ok")
        
        # Clean up other log file
        other_log = f"{self.log_file}.ok1" if log_to_use.endswith("ok2") else f"{self.log_file}.ok2"
        if os.path.exists(other_log):
            os.remove(other_log)
            
        return ec


if __name__ == "__main__":
    wrapper = TwoLSWrapper()
    wrapper.parse_arguments(sys.argv[1:])
    wrapper.execute()