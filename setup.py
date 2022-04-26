from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="anipy_gui",
    packages=find_packages(include=["anipy_gui"]),
    package_data={"anipy_gui": ["assets/*"]},
    include_package_data=True,
    version="1.0.0",
    description="GUI frontend for anipy-cli",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="sdaqo",
    author_email="sdaqo.dev@protonmail.com",
    url="https://github.com/sdaqo/anipy-gui",
    license="GPL-3.0",
    install_requires=["anipy-cli>=2.2.7", "PyQt5", "python-mpv", "desktop_file"],
    entry_points="[console_scripts]\nanipy-gui=anipy_gui.run:main",
)