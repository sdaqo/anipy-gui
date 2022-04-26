#!/bin/bash
echo "> Generating paths"
APPLIACTION_PATH="/usr/share/applications"
ICON_PATH="$(pip show anipy-gui | grep -oP "(?<=Location: ).*")/anipy_gui/assets/icon.png"
EXEC_PATH=$(which anipy-gui)

echo "> Generating .dektop file"
printf '%b\n' "[Desktop Entry]\nName=AniPy GUI\nComment=AniPy GUI\nExec=$EXEC_PATH\nIcon=$ICON_PATH\nTerminal=false\nType=Application\nCategories=Entertainment;Anime" > anipy-gui.desktop
echo "> Moving .dektop file to applicaion folder"
sudo mv anipy-gui.desktop $APPLIACTION_PATH