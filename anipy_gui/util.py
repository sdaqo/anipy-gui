import sys


def get_valid_pathname(name):
    WIN_INVALID_CHARS = ["\\", "/", ":", "*", "?", "<", ">", "|", '"']

    if sys.platform == "win32":
        name = "".join(["_" if x in WIN_INVALID_CHARS else x for x in name])
    else:
        name = name.replace("/", "_")

    return name
