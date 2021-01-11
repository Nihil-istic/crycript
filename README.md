# crycript
Python symmetric encryption tool by Salvador BG

# How to install on linux?

## 1 Download the program

Go to https://github.com/Nihil-istic/crycript

Click the green button "Code"

Click Download ZIP

If not there, move the zip file to ~/Downloads

## 2 Extract the zip file

You should now have a crycript-main folder in ~/Downloads

You can now delete the zip file:

    rm ~/Downloads/crycript-main.zip

## 3 Give executable permissions to the installer

    chmod 700 ~/Downloads/crycript-main/crycript\ installer.sh

## 4 Execute the installer

    cd ~/Downloads/crycript-main && ./crycript\ installer.sh

## 5 Install pip requirements

Make sure you have a working pip installation

    pip install -r ~/.local/opt/crycript-main/requirements.txt

# How to uninstall it on linux?

## 1 Give executable permissions to the uninstaller

    chmod 700 ~/.local/opt/crycript-main/crycript\ uninstaller.sh

## 2 Execute the uninstaller

    cd  ~/.local/opt/crycript-main/ && ./crycript\ uninstaller.sh

## 3 Modify your ~/.bashrc file

You now have:

    # Python scripts
    
    export PATH=$PATH...
    
You can now delete those two lines

# How to update?

## 1 Make a backup of encrypted files

    cp file file.bak
    
Where file is the path to the file
    
## 2 Decrypt them

    crycript -d file

## 3 Uninstall crycript (using the uninstaller) or remove old files

    rm ~/.local/opt/crycript-main/*

## 4 Follow the installation guide
    
## 5 Encrypt your files with the new version

    crycript -e file
