#!/usr/bin/env python3

import os
import sys
import subprocess
import time
from common import ToolWrapper

class CBMCWrapper(ToolWrapper):
    """CBMC-specific wrapper implementation"""
    
    def __init__(self):
        super().__init__()
        self.tool_binary = "./cbmc-binary"
        self.tool_name = "CBMC"
        self.find_options = ""
        
    def print_version(self):
        """Print CBMC version"""
        subprocess.run([self.tool_binary, "--version"])
        
    def run(self):
        """Run CBMC with unwinding"""
        # Adjust property for termination
        if self.prop == "termination":
            self.property_options += " --no-assertions --no-self-loops-to-assumptions"
            
        # Update environment
        os.environ['PROPERTY'] = self.property_options
        
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
            
        # Run CBMC with increasing unwind bounds
        os.environ['GMON_OUT_PREFIX'] = f"cbmc_{gmon_suffix}"
        
        unwind_bounds = [2, 6, 12, 17, 21, 40, 200, 400, 1025, 2049, 268435456]
        timeout_seconds = 875
        memory_limit = 15000000  # in KB
        
        start_time = time.time()
        ec = 42
        
        for unwind in unwind_bounds:
            if time.time() - start_time > timeout_seconds:
                break
                
            with open(f"{self.log_file}.latest", 'w') as log:
                log.write(f"Unwind: {unwind}\n")
                
            # First run without unwinding assertions check
            cbmc_cmd = [
                self.tool_binary,
                "--no-unwinding-assertions",
                "--no-standard-checks",
                "--graphml-witness", f"{self.log_file}.witness",
                "--slice-formula",
                "--unwind", str(unwind),
                "--stop-on-fail",
                "--object-bits", self.obj_bits
            ] + self.property_options.split() + [f"{self.log_file}.bin"]
            
            try:
                # Set memory limit using ulimit in subprocess
                result = subprocess.run(
                    ["bash", "-c", f"ulimit -v {memory_limit}; exec " + " ".join(f'"{arg}"' for arg in cbmc_cmd)],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds - (time.time() - start_time)
                )
                
                with open(f"{self.log_file}.latest", 'a') as log:
                    log.write(result.stdout)
                    log.write(result.stderr)
                    
                ec = result.returncode
                
                # Check for successful verification
                if ec == 0:
                    if "VERIFICATION SUCCESSFUL" not in result.stdout.split('\n')[-10:]:
                        ec = 1
                    else:
                        # Double-check with unwinding assertions
                        check_cmd = [
                            self.tool_binary,
                            "--slice-formula",
                            "--no-standard-checks",
                            "--unwind", str(unwind),
                            "--stop-on-fail",
                            "--object-bits", self.obj_bits
                        ] + self.property_options.split() + [f"{self.log_file}.bin"]
                        
                        check_result = subprocess.run(
                            ["bash", "-c", f"ulimit -v {memory_limit}; exec " + " ".join(f'"{arg}"' for arg in check_cmd)],
                            capture_output=True,
                            timeout=timeout_seconds - (time.time() - start_time)
                        )
                        
                        if check_result.returncode != 0:
                            ec = 42
                            
                # Check for verification failure
                elif ec == 10:
                    if "VERIFICATION FAILED" not in result.stdout.split('\n')[-10:]:
                        ec = 1
                        
                # Update log files based on result
                if ec == 0:
                    os.rename(f"{self.log_file}.latest", f"{self.log_file}.ok")
                    with open(f"{self.log_file}.ok", 'a') as log:
                        log.write(f"\nEC={ec}\n")
                    break
                elif ec == 10:
                    os.rename(f"{self.log_file}.latest", f"{self.log_file}.ok")
                    with open(f"{self.log_file}.ok", 'a') as log:
                        log.write(f"\nEC={ec}\n")
                    break
                elif ec == 42:
                    os.rename(f"{self.log_file}.latest", f"{self.log_file}.ok")
                    with open(f"{self.log_file}.ok", 'a') as log:
                        log.write(f"\nEC={ec}\n")
                else:
                    if self.ec != 0:
                        self.ec = ec
                        os.rename(f"{self.log_file}.latest", f"{self.log_file}.ok")
                    with open(f"{self.log_file}.ok", 'a') as log:
                        log.write(f"\nEC={ec}\n")
                    break
                    
            except subprocess.TimeoutExpired:
                ec = 42
                if os.path.exists(f"{self.log_file}.latest"):
                    os.rename(f"{self.log_file}.latest", f"{self.log_file}.ok")
                with open(f"{self.log_file}.ok", 'a') as log:
                    log.write(f"\nEC={ec}\n")
                break
            except Exception:
                ec = 42
                continue
                
        # Final log update if needed
        if not os.path.exists(f"{self.log_file}.ok"):
            if os.path.exists(f"{self.log_file}.latest"):
                os.rename(f"{self.log_file}.latest", f"{self.log_file}.ok")
            with open(f"{self.log_file}.ok", 'a') as log:
                log.write(f"\nEC=42\n")
                
        self.ec = ec


if __name__ == "__main__":
    wrapper = CBMCWrapper()
    wrapper.parse_arguments(sys.argv[1:])
    wrapper.execute()