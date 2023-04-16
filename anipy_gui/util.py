import sys
from appdirs import user_data_dir
from pathlib import Path

from anipy_gui.version import __appname__


def get_valid_pathname(name):
    WIN_INVALID_CHARS = ["\\", "/", ":", "*", "?", "<", ">", "|", '"']

    if sys.platform == "win32":
        name = "".join(["_" if x in WIN_INVALID_CHARS else x for x in name])
    else:
        name = name.replace("/", "_")

    return name


def get_fav_file():
    data_dir = Path(user_data_dir(__appname__, appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir / "favorites.txt"


def get_fav_list():
    fav_file = get_fav_file()

    if not fav_file.is_file():
        return []

    return fav_file.read_text().split("\n")
