import argparse
import shutil
import os
import json


def _get_my_dir(): return os.path.dirname(os.path.realpath(__file__))


def _parse_cmd_line():
    parser = argparse.ArgumentParser(
        description="The script automates the installation, removeal, and evalaution of individual versions "
                    " of CBMC in the 'benchexec' framework.")
    parser.add_argument("-V", "--version", action="store_true",
                        help="Prints a version string.")
    parser.add_argument("--install", type=str,
                         help="To add (install) a tool into 'benchexec'.")
    parser.add_argument("--remove", type=str,
                         help="To remove (uninstall) a tool from 'benchexec'.")
    parser.add_argument("--evaluate", type=str,
                         help="To start the evaluation.")
    parser.add_argument("--part", type=int,
                         help="A number of an XML file to be used.")
    parser.add_argument("--timeout", type=int,
                         help="Number of seconds reserved for analysis.")
    parser.add_argument("--tasks", nargs='+',
                         help="A list of verifications task to be performed "
                               "(a subset of tasks specied in the XML file).")
    return parser.parse_args()


def get_names_of_tools():
    return {
        "cbmc",
        "cbmc-incremental",
        "cbmc-incremental-ele",
        "cbmc-incremental-rebase",
        "cbmc-incremental-rebase-ele",
        "cbmc-sv-comp-2017-pr",
        "cbmc-sv-comp-2017-pr-rebase",
        "cbmc-symex",
        "xtest"
    }


def get_install_directories_of_tools():
    return {name: os.path.join(
                _get_my_dir(),
                "..",
                "cbmc-versions",
                name if not name.endswith("-ele") else name[:-4],
                "bin"
                )
            for name in get_names_of_tools()}


def clean_old_results():
    if os.path.isdir(os.path.join(_get_my_dir(), "results")):
        print("sudo rm -rf \"" + os.path.join(_get_my_dir(), "results") + "\"")
        os.system("sudo rm -rf \"" + os.path.join(_get_my_dir(), "results") + "\"")
    if os.path.isfile(os.path.join(_get_my_dir(), "witness.graphml")):
        print("sudo rm -f \"" + os.path.join(_get_my_dir(), "witness.graphml") + "\"")
        os.system("sudo rm -f \"" + os.path.join(_get_my_dir(), "witness.graphml") + "\"")


def install_tool(tool_name, xml_part, benchexec_tools_path):
    assert tool_name in get_names_of_tools()
    os.system("sudo cp \"" + os.path.join(get_install_directories_of_tools()[tool_name], tool_name + ".py") +
              "\" \"" + os.path.join(benchexec_tools_path, tool_name + ".py") + "\"")
    shutil.copy(os.path.join(get_install_directories_of_tools()[tool_name], tool_name),
                os.path.join(_get_my_dir(), tool_name))
    shutil.copy(os.path.join(get_install_directories_of_tools()[tool_name], tool_name + "-binary"),
                os.path.join(_get_my_dir(), tool_name + "-binary"))
    xml_part_name = "" if xml_part is None else str(xml_part)
    shutil.copy(os.path.join(get_install_directories_of_tools()[tool_name], tool_name + xml_part_name + ".xml"),
                os.path.join(_get_my_dir(), tool_name + xml_part_name + ".xml"))


def remove_tool(tool_name, xml_part, benchexec_tools_path):
    assert tool_name in get_names_of_tools()
    os.system("sudo rm -f \"" + os.path.join(benchexec_tools_path, tool_name + ".py") + "\"")
    os.remove(os.path.join(_get_my_dir(), tool_name))
    os.remove(os.path.join(_get_my_dir(), tool_name + "-binary"))
    xml_part_name = "" if xml_part is None else str(xml_part)
    os.remove(os.path.join(_get_my_dir(), tool_name + xml_part_name + ".xml"))


def evaluate_tool(tool_name, xml_part, timeout_seconds, tasks):
    assert tool_name in get_names_of_tools()
    clean_old_results()
    os.system("sudo swapoff -a")
    xml_part_name = "" if xml_part is None else str(xml_part)
    timeout_string = (" -T " + str(timeout_seconds) + "s ") if timeout_seconds is not None else ""
    tasks = (" --tasks " + " ".join(tasks)) if tasks is not None and isinstance(tasks, list) and len(tasks) > 0 else ""
    os.system(
        "sudo benchexec --no-container " +
        timeout_string +
        tool_name + xml_part_name + ".xml " +
        tasks
        )


def _main():
    cmdline = _parse_cmd_line()

    if cmdline.version:
        print("v.1.0")
        return

    benchexec_tools_path_json = os.path.join(_get_my_dir(), "benchexec_tools_path.json")
    if not os.path.isfile(benchexec_tools_path_json):
        default_benchexec_tools_path = "/usr/local/lib/python3.5/dist-packages/benchexec/tools"
        if os.path.isdir(default_benchexec_tools_path):
            benchexec_tools_path = default_benchexec_tools_path
        else:
            benchexec_tools_path = None
            for root, dir_names, _ in os.walk("/"):
                if root.endswith("/benchexec/tools"):
                    benchexec_tools_path = root
                    break
            if benchexec_tools_path is None:
                print("ERROR: Cannot find the benchexec's install dir 'dist-packages/benchexec/tools' for tools.")
                return -1
        with open(benchexec_tools_path_json, "w") as ofile:
            ofile.write(json.dumps({"benchexec_tools_path": benchexec_tools_path}, sort_keys=True, indent=4))
    with open(benchexec_tools_path_json, "r") as ifile:
        benchexec_tools_path = json.load(ifile)["benchexec_tools_path"]

    if cmdline.install is not None:
        install_tool(cmdline.install, cmdline.part, benchexec_tools_path)

    if cmdline.remove is not None:
        remove_tool(cmdline.remove, cmdline.part, benchexec_tools_path)

    if cmdline.evaluate is not None:
        evaluate_tool(cmdline.evaluate, cmdline.part, cmdline.timeout, cmdline.tasks)

    return 0


if __name__ == "__main__":
    exit(_main())

