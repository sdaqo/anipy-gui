from typing import Union, List
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


@dataclass_json
@dataclass
class ProgressList:
    progress: List[Progress]


def get_progress_file(anime_name) -> Path:
    progress_dir = Path(user_data_dir(__appname__, appauthor=False)) / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)

    progress_file = progress_dir / get_valid_pathname(anime_name)

    return progress_file.with_suffix(".json")


def get_progress(anime_name) -> List[Progress]:
    prog_file = get_progress_file(anime_name)

    if not prog_file.is_file():
        return []

    progress_list = ProgressList.from_json(prog_file.read_text())

    logger.debug(f"Getting progress of {anime_name}: {progress_list}")
    return progress_list.progress


def get_progress_episode(
    anime_name, episode: Union[int, float]
) -> Union[Progress, None]:
    prog_list = get_progress(anime_name)

    for prog in prog_list:
        if prog.episode == episode:
            return prog

    return None


def add_progress(anime_name, progress: Progress):
    logger.debug(
        f"Updating progress of episode {progress.episode} of {anime_name} to {progress.time}"
    )
    prog_file = get_progress_file(anime_name)
    prog_list = get_progress(anime_name)

    for i, prog in enumerate(prog_list):
        if prog.episode == progress.episode:
            prog_list[i] = progress
            break
    else:
        prog_list.append(progress)

    prog_file.write_text(ProgressList(progress=prog_list).to_json())
