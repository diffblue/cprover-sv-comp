import os
import argparse
import json
from xml2json import convert_xml_to_json


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


def build_stats_json_for_evaluation_dir(evaluation_data_root_dir, output_json_pathname):
    total_stats = dict()
    for xml_dir, xml_name in [(os.path.abspath(dirpath), fname)
                              for dirpath, _, filenames in os.walk(evaluation_data_root_dir)
                              for fname in filenames
                              if os.path.splitext(fname)[1].lower() == ".xml"]:
        json_pathname = os.path.join(xml_dir, os.path.splitext(xml_name)[0] + ".json")
        convert_xml_to_json(os.path.join(xml_dir, xml_name), json_pathname)
        if os.path.isfile(json_pathname):
            with open(json_pathname, "r") as ifile:
                stats = json.loads(ifile.read())
            for name, props in stats.items():
                if name in total_stats:
                    total_stats[name] += props
                else:
                    total_stats[name] = props.copy()
    with open(output_json_pathname, "w") as ofile:
        ofile.write(json.dumps(total_stats, sort_keys=True, indent=4))
    return 0


def _main(cmdline):
    retval = 0
    try:
        retval = build_stats_json_for_evaluation_dir(cmdline.input, cmdline.output)
    except:
        retval = 2
    finally:
        return retval


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
