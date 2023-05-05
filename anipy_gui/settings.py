from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pathlib import Path
from appdirs import user_config_dir

from anipy_gui.version import __appname__


def get_settings_file():
    cfg_dir = Path(user_config_dir(__appname__, appauthor=False))
    cfg_dir.mkdir(parents=True, exist_ok=True)

    cfg_file = cfg_dir / "settings.json"
    if not cfg_file.is_file():
        cfg_file.touch()
        cfg_file.write_text("{}")

    return cfg_file


@dataclass_json
@dataclass
class Settings:
    quality: str = "best"
    keep_progress: bool = True
    max_cache_size: int = -1

    def __setattr__(self, name, value):
        # Write Settings when something changes
        super().__setattr__(name, value)

        sett_file = get_settings_file()
        sett_file.write_text(self.to_json())


def load_settings() -> Settings:
    sett_file = get_settings_file()
    return Settings.from_json(sett_file.read_text())
