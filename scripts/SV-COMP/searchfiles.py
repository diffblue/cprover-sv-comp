import os
import argparse
import json
import re


def _build_command_line_interface():
    parser = argparse.ArgumentParser(
        description="TODO",
        )
    parser.add_argument("-V", "--version", action="store_true",
        help="Prints the version string of the module.")
    parser.add_argument(
        "input", type=str,
        help="TODO")
    parser.add_argument(
        "output", type=str,
        help="TODO"
        )
    cmdline = parser.parse_args()

    if cmdline.version:
        print("v.1.0")
        exit(0)

    if not os.path.isdir(cmdline.input):
        print("ERROR: In option 'input': The passed input directory does not exist.")
        exit(1)
    if os.path.isdir(cmdline.output):
        print("ERROR: In option 'output': The passed output file is an existing directory.")
        exit(1)
    if os.path.splitext(cmdline.output)[1].lower() != ".json":
        print("ERROR: In option 'input': The passed output file does not have '.json' extension.")
        exit(1)

    return cmdline


def search_benchmarks_for_fopen_and_FILE(cmdline):

    def is_desired(content):
        if "fopen" in content:
            return True
        for candidate in [" FILE ", "\tFILE ", " FILE\t", "\tFILE\t", " FILE*", "\tFILE*"]:
            if candidate in content:
                return True
        return False

    result = []
    for fdir, fname in [(os.path.abspath(dirpath), fname)
                        for dirpath, _, filenames in os.walk(cmdline.input)
                        for fname in filenames
                        if not dirpath.lower().endswith("-todo") and
                           os.path.splitext(fname)[1].lower() in [".c", ".i"]]:
        pathname = os.path.join(fdir, fname)
        with open(pathname, "r") as ifile:
            content = ifile.read()
            if is_desired(content):
                result.append(pathname)
    ifiles = [fname for fname in result if fname.endswith(".i")]
    cfiles = [fname for fname in result if fname.endswith(".c") and fname[:-2]+".i" not in ifiles]
    os.makedirs(os.path.dirname(cmdline.output), exist_ok=True)
    with open(cmdline.output, "w") as ofile:
        ofile.write(json.dumps(ifiles + cfiles, sort_keys=True, indent=4))


def search_logs_for_message(cmdline, message, category=None):
    falsification = []
    result = []
    num_log_files = 0
    for fdir, fname in [(os.path.abspath(dirpath), fname)
                        for dirpath, _, filenames in os.walk(cmdline.input)
                        for fname in filenames
                        if os.path.splitext(fname)[1].lower() == ".log"]:
        num_log_files += 1
        pathname = os.path.join(fdir, fname)
        with open(pathname, "r") as ifile:
            content = ifile.read()
            if message in content:
                benchmark = None
                matches = re.findall("^Parsing .*$", content, re.MULTILINE)
                if len(matches) == 1:
                    raw_pathname = matches[0][8:]
                    benchmark = os.path.join(os.path.basename(os.path.dirname(raw_pathname)), os.path.basename(raw_pathname))
                result.append({pathname: benchmark})
                if "_false-" + ("" if category is None else category) in benchmark:
                    falsification.append(benchmark)
    os.makedirs(os.path.dirname(cmdline.output), exist_ok=True)
    with open(cmdline.output, "w") as ofile:
        ofile.write(json.dumps({"issues": result, "falsification": sorted(falsification)}, sort_keys=True, indent=4))
    print("There was searched " + str(num_log_files) + " files.")


def search_logs_for_errors(cmdline):
    result = dict()
    num_log_files = 0
    for fdir, fname in [(os.path.abspath(dirpath), fname)
                        for dirpath, _, filenames in os.walk(cmdline.input)
                        for fname in filenames
                        if os.path.splitext(fname)[1].lower() == ".log"]:
        num_log_files += 1
        pathname = os.path.join(fdir, fname)
        with open(pathname, "r") as ifile:
            lines = ifile.readlines()

        keys = []
        for i in reversed(range(len(lines))):
            line = lines[i].strip()
            if len(line) == 0:
                continue
            keys.append(line)
            if len(keys) == 3:
                break
        if len(keys) == 0:
            key = "<OTHER>"
        else:
            key = "::".join(keys)

        benchmark = None
        for i in range(len(lines)):
            line = lines[i].strip()
            matches = re.findall("^Parsing .*$", line)
            if len(matches) == 1:
                raw_pathname = matches[0][8:]
                benchmark = os.path.join(os.path.basename(os.path.dirname(raw_pathname)),
                                         os.path.basename(raw_pathname))
                break
        if benchmark is None:
            benchmark = "UNKNOWN [log='" + pathname + "']"
            key = "<OTHER>"

        if key in result:
            result[key].append(benchmark)
        else:
            result[key] = [benchmark]

    sorted_result = {key: sorted(benchmarks) for key, benchmarks in result.items()}
    statistics = dict()
    for key, benchmarks in result.items():
        statistics[key] = len(benchmarks)

    os.makedirs(os.path.dirname(cmdline.output), exist_ok=True)
    with open(cmdline.output, "w") as ofile:
        ofile.write(json.dumps({"results": sorted_result, "statistics": statistics}, sort_keys=True, indent=4))
    print("There was searched " + str(num_log_files) + " files.")


def _main(cmdline):
    # search_benchmarks_for_fopen_and_FILE(cmdline)
    # search_logs_for_message(cmdline, "implicit conversion not permitted", "unreach-call")
    # search_logs_for_message(cmdline, "cannot unpack struct with non-byte aligned components:")
    # search_logs_for_message(cmdline, "byte_update of unknown width:")
    # search_logs_for_message(cmdline, "equality without matching types")
    # search_logs_for_message(cmdline, "={ [")
    # search_logs_for_message(cmdline, "terminate called after throwing an instance of 'int'")
    search_logs_for_message(cmdline, "Numeric exception :")
    # search_logs_for_errors(cmdline)




if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
