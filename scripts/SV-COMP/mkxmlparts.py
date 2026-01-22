import os
import shutil


def get_num_parts():
    return 23


def get_source_file():
    return os.path.abspath("cbmc.xml")


def get_destination_file(idx):
    src_file = get_source_file()
    dir_name = os.path.dirname(src_file)
    file_name = os.path.basename(src_file)
    plain_file_name, extension = os.path.splitext(file_name)
    return os.path.join(dir_name, plain_file_name + str(idx) + extension)


def update_part_file(idx):
    assert idx > 0
    with open(get_destination_file(idx), "r") as ifile:
        content = ifile.read()
    first_task_idx = content.find("<tasks name=\"")
    assert first_task_idx > 0

    my_task_idx = 0
    for i in range(idx):
        my_task_idx = content.find("<tasks name=\"", my_task_idx + len("<tasks name=\""))
        assert my_task_idx > 0
    my_task_end_idx = content.find("</tasks>", my_task_idx)
    assert my_task_end_idx > my_task_idx
    my_task_end_idx += len("</tasks>")

    tasks_end_idx = content.rfind("</benchmark>")
    assert tasks_end_idx > my_task_end_idx

    with open(get_destination_file(idx), "w") as ofile:
        ofile.write(content[:first_task_idx] + content[my_task_idx:my_task_end_idx] + "\n\n" + content[tasks_end_idx:])


def _main():
    for i in range(1, get_num_parts() + 1):
        shutil.copy(get_source_file(), get_destination_file(i))
        update_part_file(i)


if __name__ == "__main__":
    exit(_main())
