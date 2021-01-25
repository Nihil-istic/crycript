#!/usr/bin/bash
# crycript 2021.01.24 uninstaller
# source at https://github.com/Nihil-istic/crycript/

rm -vr ~/.local/opt/crycript-main
rm -v ~/.local/opt/python-scripts/crycript
rmdir -v ~/.local/opt/python-scripts
rmdir -v ~/.local/opt
echo 'Remember to delete the line: export PATH=$PATH:$HOME/.local/opt/python-scripts/ in your .bashrc if no longer needed'
