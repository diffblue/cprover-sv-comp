import os
import argparse
import glob
import json


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

    if not os.path.isfile(cmdline.input):
        print("ERROR: In option 'input': The passed input file does not exist.")
        exit(1)
    if os.path.splitext(cmdline.input)[1].lower() != ".set":
        print("ERROR: In option 'input': The passed output file does not have '.set' extension.")
        exit(1)
    if os.path.isdir(cmdline.output):
        print("ERROR: In option 'output': The passed output file is an existing directory.")
        exit(1)
    if os.path.splitext(cmdline.output)[1].lower() != ".json":
        print("ERROR: In option 'input': The passed output file does not have '.json' extension.")
        exit(1)

    return cmdline


def _main(cmdline):
    with open(cmdline.input, "r") as ifile:
        groups = ifile.readlines()
    result = {
        "set_file": os.path.basename(cmdline.input),
        "benchmarks": []
        }
    old_cwd = os.getcwd()
    for raw_group in groups:
        group = raw_group.strip()
        if len(group) == 0 or group[0] == "#":
            continue
        os.chdir(os.path.join(os.path.dirname(cmdline.input), os.path.dirname(group)))
        for fname in glob.glob(os.path.basename(group)):
            result["benchmarks"].append(os.path.join(os.path.dirname(group), fname))
    os.chdir(old_cwd)
    result["benchmarks"] = sorted(result["benchmarks"])
    os.makedirs(os.path.dirname(cmdline.output), exist_ok=True)
    with open(cmdline.output, "w") as ofile:
        ofile.write(json.dumps(result, sort_keys=True, indent=4))


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
