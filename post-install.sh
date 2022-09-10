#!/bin/bash
echo "> Generating paths"
APPLICTION_PATH="/usr/share/applications"
ICON_PATH="$(pip show anipy-gui | grep -oP "(?<=Location: ).*")/anipy_gui/assets/icon.png"
EXEC_PATH=$(which anipy-gui)

echo "> Generating .dektop file"
printf '%b\n' "[Desktop Entry]\nName=AniPy GUI\nComment=AniPy GUI\nExec=$EXEC_PATH\nIcon=$ICON_PATH\nTerminal=false\nType=Application\nCategories=Entertainment;Anime" > anipy-gui.desktop
echo "> Moving .dektop file to: $APPLICTION_PATH"
mv anipy-gui.desktop $APPLICTION_PATH
