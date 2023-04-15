from typing import Union, Iterable
from anipy_cli import history, Entry

from anipy_gui.anime import Anime


def get_history() -> Iterable[Anime]:
    hist_data = history(Entry()).read_save_data()

    for key, val in hist_data.items():
        yield Anime(
            entry=Entry(
                show_name=key,
                category_url=val["category-url"],
                ep=val["ep"],
                ep_url=val["ep-link"],
            )
        )


def write_history(anime: Anime):
    history(Anime).write_hist()
