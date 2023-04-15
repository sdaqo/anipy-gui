from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class AnimeInfo:
    show_name: str
    image_url: str
    type: str
    synopsis: str
    genres: List[str]
    release_year: int
    status: str
