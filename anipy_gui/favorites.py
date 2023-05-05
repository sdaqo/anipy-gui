from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
from appdirs import user_data_dir
from pathlib import Path

from anipy_gui.version import __appname__


@dataclass_json
@dataclass
class Favorite:
    show_name: str
    category_url: str


@dataclass_json
@dataclass
class Favorites:
    favorites: List[Favorite]


def get_fav_file():
    data_dir = Path(user_data_dir(__appname__, appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir / "favorites.json"


def get_favorites():
    fav_file = get_fav_file()
    if fav_file.exists():
        favs = Favorites.from_json(fav_file.read_text())
    else:
        favs = Favorites([])

    return favs


def add_favorite(show_name, category_url):
    fav_file = get_fav_file()
    favs = get_favorites()
    favs.favorites.append(Favorite(show_name, category_url))
    fav_file.write_text(favs.to_json())


def remove_favorite(show_name):
    fav_file = get_fav_file()
    favs = get_favorites()
    favs.favorites = [fav for fav in favs.favorites if fav.show_name != show_name]
    fav_file.write_text(favs.to_json())


def is_favorite(show_name):
    favs = get_favorites()
    for fav in favs.favorites:
        if fav.show_name == show_name:
            return True

    return False
