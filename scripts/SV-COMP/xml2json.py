import os
import argparse
import xml.etree.ElementTree
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
    if os.path.splitext(cmdline.input)[1].lower() != ".xml":
        print("ERROR: In option 'input': The passed input file does not have '.xml' extension.")
        exit(1)

    if os.path.isdir(cmdline.output):
        print("ERROR: In option 'output': The passed output file is an existing directory.")
        exit(1)
    if os.path.splitext(cmdline.output)[1].lower() != ".json":
        print("ERROR: In option 'input': The passed output file does not have '.json' extension.")
        exit(1)

    return cmdline


def convert_xml_to_json(xml_pathname, json_pathname):
    retval = 0
    benchmark_classification = dict()
    tree = xml.etree.ElementTree.parse(xml_pathname)
    for run_elem in tree.getroot().findall("run"):
        if "name" not in run_elem.attrib:
            print("WARNING: Found '<run .../>' element without 'name' attribute. Skipping it.")
            retval = 3
            continue
        name = run_elem.attrib["name"]
        if not isinstance(name, str) or len(name) == 0:
            print("WARNING: Found '<run .../>' element with wrongly formatted 'name' attribute. Skipping it.")
            retval = 3
            continue
        if "properties" not in run_elem.attrib:
            print("WARNING: Found '<run .../>' element without 'properties' attribute. Skipping it.")
            retval = 3
            continue
        properties = run_elem.attrib["properties"]
        if not isinstance(properties, str) or len(properties) == 0:
            print("WARNING: Found '<run .../>' element with wrongly formatted 'properties' attribute. Skipping it.")
            retval = 3
            continue
        if "options" not in run_elem.attrib:
            print("WARNING: Found '<run .../>' element without 'options' attribute. Skipping it.")
            retval = 3
            continue
        options = run_elem.attrib["options"]
        if not isinstance(options, str) or len(options) == 0:
            print("WARNING: Found '<run .../>' element with wrongly formatted 'options' attribute. Skipping it.")
            retval = 3
            continue
        status = None
        for child in run_elem:
            if "title" in child.attrib and child.attrib["title"] == "status" and "value" in child.attrib:
                status = child.attrib["value"]
                break
        if status is None:
            print("WARNING: Found '<run .../>' element without 'status' classification. Skipping it.")
            retval = 3
            continue
        if not isinstance(status, str):
            print("WARNING: Found '<run .../>' element with wrongly formatted 'status' attribute. Skipping it.")
            retval = 3
            continue
        if len(status) == 0:
            print("WARNING: Found '<run .../>' element with empty 'status' attribute (perhaps incomplete result). Skipping it.")
            retval = 3
            continue
        record = {
            "status": status,
            "properties": properties,
            "options": options
        }
        if name in benchmark_classification:
            benchmark_classification[name].append(record)
        else:
            benchmark_classification[name] = [record]
    with open(json_pathname, "w") as ofile:
        ofile.write(json.dumps(benchmark_classification, sort_keys=True, indent=4))
    return retval


def _main(cmdline):
    retval = 0
    try:
        retval = convert_xml_to_json(cmdline.input, cmdline.output)
    except:
        retval = 2
    finally:
        return retval


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
