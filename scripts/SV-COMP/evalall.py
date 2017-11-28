import os
import shutil
import subprocess
import time


def get_benchmarks():
    return [
        "ntdrivers/floppy2_true-unreach-call.i.cil.c",
        ]


def run_tool(command_to_execute, current_working_dir, timeout_in_seconds):
    start_time = time.time()
    process = subprocess.Popen(
        command_to_execute,
        cwd=current_working_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid
        )
    while time.time() - start_time < timeout_in_seconds:
        is_allive = process.poll()
        if is_allive is not None:
            return True, str(process.stdout.read()) + str(process.stderr.read())
        time.sleep(0.005)
    try:
        os.killpg(os.getpgid(process.pid), subprocess.signal.SIGTERM)
    except ProcessLookupError:
        if process.poll():
            print("      WARNING: failed to kill the process! (PID=" + str(process.pid) + ")")
    return False, ""


def _main():
    outdir = "./evalall_results"
    os.makedirs(outdir, exist_ok=True)
    for benchmark in get_benchmarks():
        print("Processing " + benchmark)
        # stime = time.time()
        # out, err = subprocess.Popen(["python3", "./evaluate.py", benchmark], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        # etime = time.time()
        # sss = etime - stime
        # print("Time = " + str(sss))
        # output = out.decode("utf-8") + err.decode("utf-8")

        state, output = run_tool("./evalall.sh \"" + benchmark + "\"", os.getcwd(), 3 * 60)
        if state is False:
            output = "EXECUTION OF THE TOOL FAILED!\n\n\n" + output
        print(output)

        with open(os.path.join(outdir, os.path.basename(benchmark) + ".txt"), "w") as ofile:
            ofile.write(output)
        shutil.copy("./witness", os.path.join(outdir, os.path.basename(benchmark) + ".xml"))
        print("\n\n\n")
    return 0


if __name__ == "__main__":
    exit(_main())
