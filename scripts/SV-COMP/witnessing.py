import os
import argparse
import subprocess
import shutil
import json


def _build_command_line_interface():
    parser = argparse.ArgumentParser(
        description="TODO",
        )
    parser.add_argument("-V", "--version", action="store_true",
        help="Prints the version string of the module.")
    parser.add_argument(
        "benchmarks", type=str,
        help="TODO"
        )
    parser.add_argument(
        "output", type=str,
        help="TODO"
        )
    cmdline = parser.parse_args()

    if cmdline.version:
        print("v.1.0")
        exit(0)

    if not os.path.isfile(cmdline.benchmarks):
        print("ERROR: In option 'benchmarks': The passed path does not exist: " + cmdline.benchmarks)
        exit(1)
    if os.path.splitext(cmdline.benchmarks)[1].lower() != ".json":
        print("ERROR: In option 'benchmarks': The passed file does not have '.json' extension.")
        exit(1)
    cmdline.output = os.path.abspath(cmdline.output)

    return cmdline


_this_file = os.path.abspath(__file__)
def get_script_dir():
    return os.path.dirname(_this_file)


def get_benchmarks_source_root_dir():
    return os.path.abspath(os.path.join(get_script_dir(), "..", "..", "sv-benchmarks-fork-marek-trtik", "c"))


def get_benchmarks_destination_root_dir():
    return os.path.abspath(os.path.join(get_script_dir(), "..", "..", "sv-benchmarks", "c"))


def get_cbmc_root_dir():
    return os.path.abspath(os.path.join(get_script_dir(), ".."))


def get_cpa_root_dir():
    return os.path.abspath(os.path.join(get_script_dir(), "..", "cpachecker"))


def get_cbmc_timeout_seconds():
    return 30


def _main(cmdline):
    os.makedirs(cmdline.output, exist_ok=True)
    with open(cmdline.benchmarks, "r") as ifile:
        benchmark_groups = json.loads(ifile.read())
    results = dict()
    for group_fname in benchmark_groups:
        with open(group_fname, "r") as ifile:
            group = json.loads(ifile.read())
        category = os.path.splitext(group["set_file"])[0]
        category = category[:category.find("-")]
        for benchmark in group["benchmarks"]:
            src_pathname = os.path.abspath(os.path.join(get_benchmarks_source_root_dir(), benchmark))
            dst_pathname = os.path.abspath(os.path.join(get_benchmarks_destination_root_dir(), benchmark))
            print("Processing: " + src_pathname)
            os.makedirs(os.path.dirname(dst_pathname), exist_ok=True)
            shutil.copy(src_pathname, dst_pathname)

            old_cwd = os.getcwd()

            os.chdir(get_cbmc_root_dir())
            subprocess.call(["python3", "./run.py", "--evaluate", "cbmc", "--timeout", str(get_cbmc_timeout_seconds())])

            os.chdir(get_cpa_root_dir())
            # -secureMode
            p = subprocess.Popen([
                "./scripts/cpa.sh",
                "-witnessValidation",
                "-heap", "5000m",
                "-timelimit", "90s",
                "-stats",
                "-setprop", "witness.checkProgramHash=false",
                "-setprop", "cpa.predicate.memoryAllocationsAlwaysSucceed=true",
                "-setprop", "cpa.smg.memoryAllocationFunctions=malloc,__kmalloc,kmalloc,kzalloc,kzalloc_node,ldv_zalloc,ldv_malloc",
                "-setprop", "cpa.smg.arrayAllocationFunctions=calloc,kmalloc_array,kcalloc",
                "-setprop", "cpa.smg.zeroingMemoryAllocation=calloc,kzalloc,kcalloc,kzalloc_node,ldv_zalloc",
                "-setprop", "cpa.smg.deallocationFunctions=free,kfree,kfree_const",
                "-witness", os.path.abspath(os.path.join(get_cbmc_root_dir(), "witness.graphml")),
                "-spec", os.path.join(get_benchmarks_source_root_dir(), category + ".prp"),
                "-benchmark", dst_pathname
                ],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = p.communicate()
            output_string = output.decode("utf-8")
            err_string = err.decode("utf-8")

            os.makedirs(os.path.join(cmdline.output, os.path.dirname(benchmark)), exist_ok=True)
            with open(os.path.join(cmdline.output, benchmark + ".txt"), "w") as ofile:
                ofile.write("[[STDERR]]:\n\n" + output_string + "\n\n\n\n\n\n\n\n\n\n\n\n[[STDERR]]:\n\n" + err_string)

            result_start_index = output_string.find("Verification result:")
            if result_start_index != -1:
                result_end_index = output_string.find("\n", result_start_index)
                key = output_string[result_start_index:result_end_index]
            else:
                key = "<<OTHER>>"
            if key in results:
                results[key].append(benchmark)
            else:
                results[key] = [benchmark]

            shutil.rmtree(os.path.dirname(dst_pathname))
            os.chdir(old_cwd)

    results["statistics"] = {}
    for key, values in results.items():
        if key != "statistics":
            results["statistics"][key] = len(values)
    with open(os.path.join(cmdline.output, "witnessing_results.json"), "w") as ofile:
        ofile.write(json.dumps(results, sort_keys=True, indent=4))


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
