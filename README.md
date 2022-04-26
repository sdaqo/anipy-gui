

https://user-images.githubusercontent.com/63876564/165341897-a89cd315-8067-4462-ac53-47c903b3207d.mp4

# anipy-gui

A very simple GUI frontend for [anipy-cli](https://github.com/sdaqo/anipy-cli). (WIP, expect bugs)

As of now this only supports linux because libmpv on windows sucks.


# Installation

Prerequisits: [mpv](https://mpv.io) and libmpv but that should ship with mpv on install.
```
$ git clone https://github.com/sdaqo/anipy-gui

$ cd anipy-gui

$ pip install .

$ ./post-install.sh To Create Desktop file so it shows up in the start menu
```
## Uninstall

`pip uninstall anipy-gui`

To remove the desktop file clone the repository again or use your already cloned one and execute `./remove-desktop-entry.sh`

# Player and App Shortcuts

Generaly, in the Player the [standart mpv shortcuts](https://mpv.io/manual/master/#keyboard-control) are applied, there are some exceptions though:

| Action            |  Key   |                    Scope |
| ----------------- | :----: | -----------------------: |
| History           | Ctrl+H | Everywhere except player |
| Quit Player       |   q    |                   player |
| Fullscreen Player |   f/player button    |                   player |
| Next Episode      |   n    |                   player |
| Previous Episode  |   b    |                   player |
| Hide Cursor       |   h    |                   player |
