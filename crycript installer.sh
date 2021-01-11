mkdir -pv ~/.local/opt/python-scripts
mv -vi ~/Downloads/crycript-main ~/.local/opt
chmod 600 ~/.local/opt/crycript-main/sources/*
chmod 700 ~/.local/opt/crycript-main/sources/crycript_main.py
ln -s ~/.local/opt/crycript-main/sources/crycript_main.py ~/.local/opt/python-scripts/crycript
echo '# Python Scripts' >> ~/.bashrc
echo 'export PATH=$PATH":$HOME/.local/opt/python-scripts/' >> ~/.bashrc
mkdir -pv ~/.local/share/applications
mv -vi ~/.local/opt/crycript-main/crycript.desktop ~/.local/share/applications/crycript.desktop
chmod 700 ~/.local/share/applications/crycript.desktop
rm -v ~/.local/opt/crycript-main/crycript\ installer.sh
echo "Icon=$HOME/.local/opt/crycript-main/icon/chameleon.png" >> ~/.local/share/applications/crycript.desktop
