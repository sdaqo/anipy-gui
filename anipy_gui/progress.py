from typing import Union
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from appdirs import user_data_dir
from pathlib import Path
from loguru import logger

from anipy_gui.util import get_valid_pathname
from anipy_gui.version import __appname__


@dataclass_json
@dataclass
class Progress:
    episode: Union[int, float]
    time: Union[int, float]


def get_progress_file(anime_name) -> Path:
    progress_dir = Path(user_data_dir(__appname__, appauthor=False)) / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)

    progress_file = progress_dir / get_valid_pathname(anime_name)

    return progress_file.with_suffix(".json")


def get_progress(anime_name) -> Union[Progress, None]:
    prog_file = get_progress_file(anime_name)

    if not prog_file.is_file():
        return None

    progress = Progress.from_json(prog_file.read_text())

    logger.debug(f"Getting progress of {anime_name}: {progress}")
    return progress


def set_progress(anime_name, progress: Progress):
    logger.debug(f"Updating progress of {anime_name} to {progress}")
    prog_file = get_progress_file(anime_name)
    prog_file.write_text(progress.to_json())
