import os
import argparse
import json


def _build_command_line_interface():
    parser = argparse.ArgumentParser(
        description="TODO",
        )
    parser.add_argument("-V", "--version", action="store_true",
        help="Prints the version string of the module.")
    parser.add_argument(
        "left", type=str,
        help="TODO")
    parser.add_argument(
        "right", type=str,
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

    if os.path.isdir(cmdline.left):
        print("ERROR: In option 'left': The passed file is an existing directory.")
        exit(1)
    if os.path.splitext(cmdline.left)[1].lower() != ".json":
        print("ERROR: In option 'left': The passed file does not have '.json' extension.")
        exit(1)

    if os.path.isdir(cmdline.right):
        print("ERROR: In option 'right': The passed file is an existing directory.")
        exit(1)
    if os.path.splitext(cmdline.right)[1].lower() != ".json":
        print("ERROR: In option 'right': The passed file does not have '.json' extension.")
        exit(1)

    if os.path.isdir(cmdline.output):
        print("ERROR: In option 'output': The passed output file is an existing directory.")
        exit(1)
    if os.path.splitext(cmdline.output)[1].lower() != ".json":
        print("ERROR: In option 'output': The passed output file does not have '.json' extension.")
        exit(1)

    return cmdline


def parse_category_from_properties(props):
    return props.strip().split(" ")


def parse_correct_status_int(benchmark_name, suffix):
    idx_true = os.path.basename(benchmark_name).find("_true-" + suffix)
    if idx_true != -1:
        return 1
    if os.path.basename(benchmark_name).find("_false-" + suffix) == -1 and suffix == "valid-memtrack":
        return parse_correct_status_int(benchmark_name, "valid-memsafety")
    if not(os.path.basename(benchmark_name).find("_false-" + suffix) != -1):
        return None
    return 0


def status_to_int(status, suffix):
    if status is None:
        return None
    if status.lower() == "out of memory" or status.lower().startswith("error"):
        return 2
    if status.lower() == "true" or status.lower() == "true(" + suffix + ")":
        return 1
    if not (status.lower() == "false" or status.lower() == "false(" + suffix + ")") and suffix == "valid-memtrack":
        return status_to_int(status, "valid-memsafety")
    if not(status.lower() == "false" or status.lower() == "false(" + suffix + ")"):
        return 2
    return 0


def compare_status_values(correct_value, left_value, right_value):
    if left_value == right_value:
        return 0 if left_value == correct_value else 3
    else:
        return 1 if left_value == correct_value else 2


def build_diff_of_json_stats(left_json_pathname, right_json_pathname, output_json_pathname):
    with open(left_json_pathname, "r") as ifile:
        left = json.loads(ifile.read())
    with open(right_json_pathname, "r") as ifile:
        right = json.loads(ifile.read())

    unique_left = dict()
    unique_right = dict()
    both_equal_correct = dict()
    both_equal_wrong = dict()
    better_left = dict()
    better_right = dict()
    none_left = dict()
    none_right = dict()
    none_both = dict()
    for name in left.keys() | right.keys():
        if name not in left:
            assert name in right
            unique_right[name] = right[name]
        elif name not in right:
            unique_left[name] = left[name]
        else:
            diff_props = dict()
            for left_props in left[name]:
                key = (left_props["options"], left_props["properties"])
                assert key not in diff_props
                diff_props[key] = {"left": left_props["status"], "right": None}
            for right_props in right[name]:
                key = (right_props["options"], right_props["properties"])
                if key in diff_props:
                    diff_props[key]["right"] = right_props["status"]
                else:
                    diff_props[key] = {"left": None, "right": right_props["status"]}

            for config, statuses in diff_props.items():
                for category in parse_category_from_properties(config[1]):
                    correct_value = parse_correct_status_int(name, category)
                    if correct_value is None:
                        print("WARNING: cannot parse correct status from category " + str(category) + " for benchmark " + str(name))
                        continue
                    left_value = status_to_int(statuses["left"], category)
                    right_value = status_to_int(statuses["right"], category)
                    if left_value is None and right_value is None:
                        output_collection = none_both
                    elif left_value is None:
                        output_collection = none_left
                    elif right_value is None:
                        output_collection = none_right
                    else:
                        comparison_result = compare_status_values(correct_value, left_value, right_value)
                        if comparison_result == 0:
                            output_collection = both_equal_correct
                        elif comparison_result == 1:
                            output_collection = better_left
                        elif comparison_result == 2:
                            output_collection = better_right
                        else:
                            output_collection = both_equal_wrong
                    output_collection[name] = {
                        "options": config[0],
                        "properties": config[1],
                        "category": category,
                        "left_status": "NOT-PRESENT" if statuses["left"] is None else statuses["left"],
                        "left_status_value": "N/A" if left_value is None else left_value,
                        "right_status": "NOT-PRESENT" if statuses["right"] is None else statuses["right"],
                        "right_status_value": "N/A" if right_value is None else right_value
                    }
    result_diff = {
        "unique_left": unique_left,
        "unique_right": unique_right,
        "both_equal_correct": both_equal_correct,
        "both_equal_wrong": both_equal_wrong,
        "better_left": better_left,
        "better_right": better_right,
        "none_left": none_left,
        "none_right": none_right,
        "none_both": none_both,
        "statistics": {
            "num_left": len(left),
            "num_left_tasks": sum(len(values) for _, values in left.items()),
            "num_right": len(right),
            "num_right_tasks": sum(len(values) for _, values in right.items()),
            "num_unique_left": len(unique_left),
            "num_unique_right": len(unique_right),
            "num_both_equal_correct": len(both_equal_correct),
            "num_both_equal_wrong": len(both_equal_wrong),
            "num_better_left": len(better_left),
            "num_better_right": len(better_right),
            "num_none_left": len(none_left),
            "num_none_right": len(none_right),
            "num_none_both": len(none_both),
            "num_diffs": (
                len(unique_left) +
                len(unique_right) +
                len(both_equal_correct) +
                len(both_equal_wrong) +
                len(better_left) +
                len(better_right) +
                len(none_left) +
                len(none_right) +
                len(none_both)
                ),
        }

    }
    os.makedirs(os.path.dirname(output_json_pathname), exist_ok=True)
    with open(output_json_pathname, "w") as ofile:
        ofile.write(json.dumps(result_diff, sort_keys=True, indent=4))
    return 0


def _main(cmdline):
    return build_diff_of_json_stats(cmdline.left, cmdline.right, cmdline.output)
    # retval = 0
    # try:
    #     retval = build_diff_of_json_stats(cmdline.left, cmdline.right, cmdline.output)
    # except:
    #     retval = 2
    # finally:
    #     return retval


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
