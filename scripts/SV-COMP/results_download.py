import os


for name, ip in [
        ("sv-comp-cbmc-incremental-ele-part1",          "35.195.26.50"),
        ("sv-comp-cbmc-incremental-ele-part2",          "35.195.8.91"),
        ("sv-comp-cbmc-incremental-part1",              "35.195.116.95"),
        ("sv-comp-cbmc-incremental-part2",              "104.199.93.208"),
        ("sv-comp-cbmc-incremental-rebase-ele-part1",   "35.189.240.44"),
        ("sv-comp-cbmc-incremental-rebase-ele-part2",   "104.155.32.99"),
        ("sv-comp-cbmc-incremental-rebase-part1",       "35.187.83.211"),
        ("sv-comp-cbmc-incremental-rebase-part2",       "104.199.79.254"),
        ("sv-comp-cbmc-part1",                          "35.195.222.120"),
        ("sv-comp-cbmc-part2",                          "192.158.29.5"),
        ("sv-comp-cbmc-sv-comp-2017-pr-part1",          "35.195.150.6"),
        ("sv-comp-cbmc-sv-comp-2017-pr-part2",          "35.195.99.239"),
        ("sv-comp-cbmc-sv-comp-2017-pr-rebase-part1",   "104.199.17.173"),
        ("sv-comp-cbmc-sv-comp-2017-pr-rebase-part2",   "35.195.208.163"),
        ("sv-comp-cbmc-symex-part1",                    "35.195.185.16"),
        ("sv-comp-cbmc-symex-part2",                    "35.195.42.83")
        ]:
    user_name = "marek_trtik"
    dst_dir = os.path.join(
        "RESULTS",
        "NOW",
        name[len("sv-comp-"):min(name.rfind("-ele") if "-ele" in name else len(name),
                                 name.rfind("-part") if "-part" in name else len(name))],
        "results"
        )
    os.makedirs(dst_dir, exist_ok=True)
    command_prefix = "scp " + user_name + "@" + ip + ":" + "~/evaluation-root/results/*."
    command_suffix = " " + dst_dir
    print("Retrieving results for " + name + " from " + ip)
    # print("Executing: " + command)
    retval = os.system(command_prefix + "bz2" + command_suffix)
    if retval != 0:
        retval = os.system(command_prefix + "xml" + command_suffix)
        if retval != 0:
            print("    ERROR: The download has failed!")

