rm -Ivr ~/.local/opt/crycript-main
rm -v ~/.local/opt/python-scripts/crycript
rmdir -v ~/.local/opt/python-scripts
rmdir -v ~/.local/opt
rm -v ~/.local/share/applications/crycript.desktop
echo "Remember to delete the line: export PATH=$PATH:$HOME/.local/opt/python-scripts/ in your .bashrc if no longer needed"
