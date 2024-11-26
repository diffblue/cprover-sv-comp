import os
import sys
import traceback
import shutil
import argparse
import json
import re


def _get_this_script_dir():
    return os.path.dirname(__file__)


def _get_cbmc_new_repo_dir():
    return os.path.abspath(os.path.join(_get_this_script_dir(), "cbmc-fork-marek-trtik"))


def _get_cbmc_new_binary():
    return os.path.abspath(os.path.join(_get_cbmc_new_repo_dir(), "src", "cbmc", "cbmc"))


def _get_installed_cbmc_new_binary():
    return os.path.abspath(os.path.join(_get_this_script_dir(), "cbmc-sv-comp-2017-pr-rebase-binary"))


def _get_cbmc_new_shell_script():
    return _get_installed_cbmc_new_binary()[:_get_installed_cbmc_new_binary().rfind("-binary")]


def _get_cbmc_old_repo_dir():
    return os.path.abspath(os.path.join(_get_this_script_dir(), "cbmc-fork-tautschnig"))


def _get_cbmc_old_binary():
    return os.path.abspath(os.path.join(_get_cbmc_old_repo_dir(), "src", "cbmc", "cbmc"))


def _get_installed_cbmc_old_binary():
    return os.path.abspath(os.path.join(_get_this_script_dir(), "cbmc-sv-comp-2017-pr-binary"))


def _get_cbmc_old_shell_script():
    return _get_installed_cbmc_old_binary()[:_get_installed_cbmc_old_binary().rfind("-binary")]


def _get_benchmarks_root_dir():
    return os.path.abspath(os.path.join(_get_this_script_dir(), "..", "sv-benchmarks", "c"))


def _get_results_diff_json_pathname():
    return os.path.abspath(os.path.join(_get_this_script_dir(), "..", "RESULTS", "diff_CBMC-sv-comp-2017-pr-rebase_CBMC-sv-comp-2017-pr.json"))


def _build_command_line_interface():
    parser = argparse.ArgumentParser(
        description="TODO",
        )
    parser.add_argument("-V", "--version", action="store_true",
        help="Prints the version string of the module.")
    parser.add_argument(
        "benchmark", type=str,
        help="TODO")
    parser.add_argument(
        "--old-cbmc", action="store_true",
        help="TODO"
        )
    cmdline = parser.parse_args()

    if cmdline.version:
        print("v.1.0")
        exit(0)

    if not os.path.isfile(cmdline.benchmark):
        if not os.path.isfile(os.path.join(_get_benchmarks_root_dir(), cmdline.benchmark)):
            print("ERROR: In option 'benchmark': The passed path does not reference an existing file.")
            exit(1)
        else:
            cmdline.benchmark = os.path.join(_get_benchmarks_root_dir(), cmdline.benchmark)
    cmdline.benchmark = os.path.abspath(cmdline.benchmark)

    return cmdline


"""
def get_cbmc_command_line_options():
    return "--graphml-witness witness.graphml --32 --propertyfile ../sv-benchmarks/c/ReachSafety.prp ../sv-benchmarks/c/eca-rers2012/Problem01_label00_true-unreach-call.c
           "--graphml-witness $LOG.witness --unwind $c --stop-on-fail $BIT_WIDTH $PROPERTY --function $ENTRY $BM"

* executing the following command:
    grep "^bitvector/.*unreach-call" *.set
  in '../sv-benchmarks/c' produces:
    ReachSafety-BitVectors.set:bitvector/*_false-unreach-call*.i
    ReachSafety-BitVectors.set:bitvector/*_true-unreach-call*.i
    ReachSafety-BitVectors.set:bitvector/*_false-unreach-call*.BV.c.cil.c
    ReachSafety-BitVectors.set:bitvector/*_true-unreach-call*.c.cil.c
  where I found the strings "bitvector" and "unreach-call" in the JSON file:
                                   ========== This is the string
    "better_right": {              v
        "../../sv-benchmarks/c/bitvector/modulus_true-unreach-call_true-no-overflow.i": {
            "category": "unreach-call",
            "left_status": "ERROR (42)",
            "left_status_value": 2,
            "options": "--32",              <======= This is the option for the shell script
            "properties": "unreach-call",           <======= This is the string
            "right_status": "true",
            "right_status_value": 1
        },

  I should thus call the shell script:
    /home/marek/root/SV-COMP-2018/BUG_FIXING/cbmc-sv-comp-2017-pr-rebase
  with these options
    ./cbmc-sv-comp-2017-pr-rebase --graphml-witness witness.graphml ${options} --propertyfile ${propertyfile} ${benchmark}
  where
    ${options}=--32                                                                         (this was taken from the JSON file, see above)
    ${propertyfile}=../sv-benchmarks/c/ReachSafety.prp                                      (this was obtained from the result of the grep command)
    ${benchmark}=../sv-benchmarks/c/eca-rers2012/Problem01_label00_true-unreach-call.c      (this was taken from the JSON file, see above)

"""


def _install_cbmc(use_old_cbmc):
    repo_dir = _get_cbmc_old_repo_dir() if use_old_cbmc else _get_cbmc_new_repo_dir()
    cbmc_binary = _get_cbmc_old_binary() if use_old_cbmc else _get_cbmc_new_binary()
    cbmc_installed_binary = _get_installed_cbmc_old_binary() if use_old_cbmc else _get_installed_cbmc_new_binary()
    if os.path.isfile(cbmc_installed_binary):
        os.remove(cbmc_installed_binary)
    old_cwd = os.getcwd()
    os.chdir(repo_dir)
    command = "make -C src"
    print("EXECUTING: IN[" + repo_dir + "]: " + command)
    retval = os.system(command)
    os.chdir(old_cwd)
    if retval != 0:
        print("ERROR: execution of the last shell command has FAILED.")
        return retval
    shutil.copy(cbmc_binary, cbmc_installed_binary)
    return 0


def _load_diff_record_of_benchmark(benchmark_pathname):
    with open(_get_results_diff_json_pathname(), "r") as ifile:
        diff = json.loads(ifile.read())
    assert "better_right" in diff
    record_name = os.path.relpath(benchmark_pathname, _get_benchmarks_root_dir())
    assert record_name in diff["better_right"]
    record = diff["better_right"][record_name]
    return record


def _get_property_file(benchmark_pathname, raw_benchmark_category):
    benchmark_dirname = os.path.dirname(os.path.relpath(benchmark_pathname, _get_benchmarks_root_dir()))
    benchmark_category = raw_benchmark_category if raw_benchmark_category != "valid-memtrack" else "valid-memsafety"
    for pathname in [os.path.abspath(os.path.join(_get_benchmarks_root_dir(), fname))
                     for fname in os.listdir(_get_benchmarks_root_dir())
                     if os.path.splitext(fname)[1] == ".set"]:
        with open(pathname, "r") as ifile:
            content = ifile.read()
            if re.findall("^" + benchmark_dirname + "/.*" + benchmark_category, content, re.MULTILINE):
                property_file_pathname = os.path.splitext(pathname)[0] + ".prp"
                if os.path.isfile(property_file_pathname):
                    return property_file_pathname
                property_file_pathname_ex = os.path.join(
                    os.path.dirname(pathname),
                    os.path.basename(pathname)[:os.path.basename(pathname).find("-")] + ".prp"
                    )
                if os.path.isfile(property_file_pathname_ex):
                    return property_file_pathname_ex
                print("ERROR: the property file " + property_file_pathname + " of the found corresponding file " +
                      pathname + " does not exist. Skipping the file.")
                print("ERROR: the property file " + property_file_pathname_ex + " of the found corresponding file " +
                      pathname + " does not exist. Skipping the file.")
    print("ERROR: cannot find any property file (*.set) for the benchmark " + benchmark_pathname +
          " and the category " + benchmark_category)
    assert False


def _evaluate_benchmark(benchmark_pathname, use_old_cbmc):
    assert isinstance(benchmark_pathname, str)
    assert isinstance(use_old_cbmc, bool)

    retval = _install_cbmc(use_old_cbmc)
    if retval != 0:
        return retval
    record = _load_diff_record_of_benchmark(benchmark_pathname)
    cbmc_script = _get_cbmc_old_shell_script() if use_old_cbmc else _get_cbmc_new_shell_script()
    property_file = _get_property_file(benchmark_pathname, record["category"])

    command = (
        cbmc_script + " " +
        "--graphml-witness witness witness.graphml " +
        "--propertyfile " + property_file + " " +
        record["options"] + " " +
        benchmark_pathname
    )
    print("EXECUTING: IN[" + os.getcwd() + "]: " + command)
    return os.system(command)


def _main(cmdline):
    retval = 0
    try:
        retval = _evaluate_benchmark(cmdline.benchmark, cmdline.old_cbmc)
    except:
        print("ERROR: An exception was raised:")
        traceback.print_exc(file=sys.stdout)
        retval = 2
    finally:
        return retval


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
