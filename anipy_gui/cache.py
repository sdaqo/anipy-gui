import shutil
import requests
from typing import Union
from pathlib import Path
from appdirs import user_cache_dir
from loguru import logger


from anipy_gui.anime_info import AnimeInfo
from anipy_gui.util import get_valid_pathname
from anipy_gui.version import __appname__
from anipy_gui.gui.util import get_icon_path


def get_cache_dir(name):
    cache_dir = Path(user_cache_dir(__appname__, appauthor=False)) / name
    cache_dir.mkdir(exist_ok=True, parents=True)

    return cache_dir


def image_from_cache(anime_name) -> Union[Path, None]:
    logger.debug(f"Accsessing image cache for {anime_name}")
    image = get_cache_dir("images") / get_valid_pathname(anime_name)

    if image.is_file():
        return image
    else:
        return None


@logger.catch(default=get_icon_path("no-image.jpg"))
def download_image_to_cache(anime_name: str, url: str) -> Path:
    image_path = get_cache_dir("images") / get_valid_pathname(anime_name)

    req = requests.get(url, stream=True)

    with image_path.open("wb") as file:
        req.raw.decode_content = True
        shutil.copyfileobj(req.raw, file)

    logger.debug(f"Cached image from {anime_name} with url {url} to {image_path}.")
    return image_path


def info_from_cache(anime_name) -> Union[AnimeInfo, None]:
    logger.debug(f"Accsessing info cache for {anime_name}")
    info_file = get_cache_dir("info") / get_valid_pathname(anime_name)
    info_file = info_file.with_suffix(".json")

    if not info_file.is_file():
        return None

    return AnimeInfo.from_json(info_file.read_text())


def info_to_cache(anime_info: AnimeInfo) -> Path:
    info_file = get_cache_dir("info") / get_valid_pathname(anime_info.show_name)
    info_file = info_file.with_suffix(".json")
    info_file.write_text(anime_info.to_json())

    logger.debug(f"Cached info from {anime_info.show_name} to {info_file}.")
    return info_file
