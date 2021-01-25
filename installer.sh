#!/usr/bin/bash
# crycript 2021.01.24 installer
# source at https://github.com/Nihil-istic/crycript/

mkdir -pv ~/.local/opt/python-scripts
mv -vi ../crycript-main ~/.local/opt
chmod 600 ~/.local/opt/crycript-main/src/*
chmod 700 ~/.local/opt/crycript-main/src/crycript_argparse.py
ln -s ~/.local/opt/crycript-main/src/crycript_argparse.py ~/.local/opt/python-scripts/crycript
echo >> ~/.bashrc
echo '# Python Scripts' >> ~/.bashrc
echo 'export PATH=$PATH":$HOME/.local/opt/python-scripts/"' >> ~/.bashrc
rm -v ~/.local/opt/crycript-main/installer.sh
