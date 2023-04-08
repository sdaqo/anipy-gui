from pathlib import Path


def get_template_path(template_name: str) -> str:
    directory = Path(__file__).parent / "templates"
    return str(directory / template_name)

def get_icon_path(icon_name: str) -> str:
    directory = Path(__file__).parent / "icons"
    return str(directory / icon_name)
