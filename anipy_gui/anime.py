from anipy_cli import Entry, videourl, epHandler, get_anime_info
from typing import List, Union
from pathlib import Path
from copy import deepcopy
from loguru import logger
from appdirs import user_data_dir

from anipy_gui.progress import Progress, set_progress, get_progress
from anipy_gui.anime_info import AnimeInfo
from anipy_gui.settings import load_settings
from anipy_gui.version import __appname__
from anipy_gui.util import get_fav_list, get_fav_file
from anipy_gui.cache import (
    info_from_cache,
    info_to_cache,
    image_from_cache,
    download_image_to_cache,
)


class Anime(Entry):
    def __init__(self, show_name: str, category_url: str, *args, **kwargs):
        super().__init__(
            show_name=show_name, category_url=category_url, *args, **kwargs
        )

        self.settings = load_settings()

    def get_is_favorite(self) -> bool:
        fav_list = get_fav_list() 

        return self.show_name in fav_list

    def get_episodes(self):
        temp_entry = Entry(category_url=self.category_url)
        return epHandler(temp_entry)._load_eps_list()

    @logger.catch(default=None)
    def get_video_link(self, episode) -> Union[str, None]:
        temp_entry = Entry(category_url=self.category_url, ep=episode)

        ep_cls = epHandler(temp_entry)
        ep_cls.gen_eplink()
        temp_entry = ep_cls.get_entry()

        vid_cls = videourl(temp_entry, self.settings.quality)
        vid_cls.stream_url()
        temp_entry = vid_cls.get_entry()

        logger.debug(
            f"Got video-url for {self.show_name} episode {episode}: {temp_entry.stream_url}"
        )
        return temp_entry.stream_url

    def get_anime_info(self) -> AnimeInfo:
        cached_info = info_from_cache(self.show_name.anime_name)

        if cached_info:
            return cached_info

        info = get_anime_info(self.category_url)
        info["show_name"] = self.show_name

        info = AnimeInfo.from_dict(info)
        info_to_cache(info)

        return info

    def get_progress(self) -> Progress:
        return get_progress(self.show_name)

    def get_image(self) -> Path:
        cached_img = image_from_cache(self.show_name)

        if cached_img:
            return cached_img

        img_url = self.get_anime_info().image_url
        img_path = download_image_to_cache(self.show_name, img_url)

        return img_path

    def set_favorite(self, is_favorite: bool):
        fav_list = get_fav_list() 
        fav_file = get_fav_file()

        if not self.show_name in fav_list:
            fav_list.append(self.show_name)

        with fav_file.open("w") as file:
            for i in fav_list:
                file.write(i + "\n")

    def set_progress(self, progress: Progress):
        set_progress(self.show_name, progress)