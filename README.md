# crycript
Python symmetric encryption tool by Salvador BG

# How to use it?

Download the program and then follow the instructions

    Go to https://github.com/Nihil-istic/crycript
    Click the green button "Code"
    Click Download ZIP

## On linux:

### 1.-

Create a directory where crycript will be located,
for example:

    $ mkdir -pv ~/.local/opt/python-scripts
    
### 2.-

Move your downloaded zip to the new location:

    $ mv -vi ~/Downloads/crycript-main.zip ~/.local/opt/python-scripts/
    
### 3.-

Extract the contents of the zip file.
You can now delete the original zip file as it will be not longer needed.

### 4.-

cd to the new directory

    $ cd ~/.local/opt/python-scripts/crycript-main

### 5.-

Make sure you have the right permissions setup

    $ chmod 0600 *

    $ chmod 0700 crycript.py
    
### 6.-

Install requirements.txt

    $ pip install -r requirements.txt

### 7.-

Change the line " #!shebang " on crycript.py to your desired shebang (it usually is " #!/usr/bin/env python ")

### 8.-

Add to your .bashrc (or .profile) the line: export PATH=$PATH":$HOME/.local/opt/python-scripts/crycript-main"

    $ echo 'export PATH=$PATH":$HOME/.local/opt/python-scripts/crycript-main"' >> ~/.bashrc

### 9.-

Open a new terminal and type

    $ crycript.py

If you get the following message:

    usage: crycript.py [-h] [-v] [-e | -d] path
    crycript.py: error: the following arguments are required: path

You have your program ready to go!

### 10.-

To see usage type:

    $ crycript.py --help
