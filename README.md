# crycript
Python symmetric encryption tool by Salvador BG

# How to use it?

Download the program and then follow the instructions

    Go to https://github.com/Nihil-istic/crycript
    Click the green button "Code"
    Click Download ZIP

## On linux:

### 1 Create a directory where crycript will be located:

    mkdir -pv ~/.local/opt/python-scripts
    
### 2 Move your downloaded zip to ~/.local/opt/:

    mv -vi ~/Downloads/crycript-main.zip ~/.local/opt
    
### 3 Extract the contents of the zip file.

You can now delete the original zip file as it will be not longer needed.

### 4 Make sure you have the right permissions setup

    chmod 0600 ~/.local/opt/crycript-main/*

    chmod 0700 ~/.local/opt/crycript-main/crycript.py
    
### 5 Add simbolic link (for a cleaner setup)

    ln -s ~/.local/opt/crycript-main/crycript.py ~/.local/opt/python-scripts/crycript

### 7 Make sure the default shebang (#!/usr/bin/env python) will work for you (python 3.9), if not, change it as needed.

### 8 Add to your .bashrc the line: export PATH=$PATH":$HOME/.local/opt/python-scripts/"

    echo '# Python Scripts' >> ~/.bashrc
    echo 'export PATH=$PATH":$HOME/.local/opt/python-scripts/' >> ~/.bashrc

### 9 Open a new terminal and type

    crycript

If you get the following message:

    usage: crycript [-h] [-v] [-p] [-e | -d | -c] path
    crycript: error: the following arguments are required: path

You have your script ready to go!

### 10 To see usage type:

    crycript.py --help

# How to update?

## 1 Make a backup of encrypted files

    cp file file.bak
    
Where <file> is the path to the file
    
## 2 Decrypt them

    crycript -d file

## 3 Remove old crycript files

    rm ~/.local/opt/crycript-main/*

## 4 Download the new zip file

Then paste its contents in ~/.local/opt/crycript-main/

## 4 Make sure you have the right permission setup

    chmod 0600 ~/.local/opt/crycript-main/*
    chmod 0700 ~/.local/opt/crycript-main/crycript.py
    
## 5 Encrypt your files with the new version

    crycript -e file
