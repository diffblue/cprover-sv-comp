import argparse
import os
import glob
import bz2


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
        "--erase-packages", action='store_true',
        help="TODO")
    cmdline = parser.parse_args()

    if cmdline.version:
        print("v.1.0")
        exit(0)

    if not os.path.isdir(cmdline.input):
        print("ERROR: In option 'input': The passed input directory does not exist.")
        exit(1)

    return cmdline


def _main(cmdline):
    old_cwd = os.getcwd()
    os.chdir(cmdline.input)
    for fname in glob.glob("*.xml.bz2"):
        with open(fname, "rb") as ifile:
            compressed_data = ifile.read()
        data = bz2.decompress(compressed_data)
        dst_fname = os.path.splitext(fname)[0]
        with open(dst_fname, "wb") as ofile:
            ofile.write(data)
        if cmdline.erase_packages:
            os.remove(fname)
    os.chdir(old_cwd)


if __name__ == "__main__":
    exit(_main(_build_command_line_interface()))
