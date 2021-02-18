# crycript
Python symmetric encryption tool by SalvadorBG

# How to install?

## 1 Download crycript

Go to https://github.com/Nihil-istic/crycript

Click the green button "Code"

Click Download ZIP

If not there, move the zip file to ~/Downloads

## 2 Extract the downloaded zip file

You should now have a crycript-main directory

You can delete the zip file

## 3 Create a directory for crycript

    mkdir -pv ~/.local/opt/python-scripts
    
## 4 Move crycript-main to its new directory

    mv -v ~/Downloads/crycript-main ~/.local/opt

## 5 Give executable permissions to CrycriptCLI.py

    chmod 700 ~/.local/opt/crycript-main/src/CrycriptCLI.py

## 6 Create a symbolic link

    ln -s ~/.local/opt/crycript-main/src/CrycriptCLI.py ~/.local/opt/python-scripts/crycript

## 7 Add python-scripts to $PATH

    echo >> ~/.bashrc
    
    echo '# Python Scripts' >> ~/.bashrc
    
    echo 'export PATH=$PATH":$HOME/.local/opt/python-scripts/"' >> ~/.bashrc

## 8 Install requirements.txt

Make sure you have a working pip installation for python3

    pip install -r ~/.local/opt/crycript-main/requirements.txt
    
Or

    pip3 install -r ~/.local/opt/crycript-main/requirements.txt

Or 
    
    pip3.9 install -r ~/.local/opt/crycript-main/requirements.txt

## 9 Test your installation

    crycript -v

If the ouput is the crycript version (a date with the format YYYY.MM.DD), you are ready to go!


# How to uninstall?

## 1 Uninstall pip requirements

    pip uninstall -r ~/.local/opt/crycript-main/requirements.txt

Or

    pip3 uninstall -r ~/.local/opt/crycript-main/requirements.txt

Or

    pip3.9 uninstall -r ~/.local/opt/crycript-main/requirements.txt

## 2 Remove the crycript directory and its contents

    rm -vr ~/.local/opt/crycript-main

## 3 Remove the symbolic link

    rm -v ~/.local/opt/python-scripts/crycript
    
## 4 If no longer needed, remove the empty python-scripts directory

    rmdir -v ~/.local/opt/python-scripts
    
## 5 If no longer needed, remove the empty opt directory

    rmdir -v ~/.local/opt
    
## 6 If no longer needed, remove the empty .local directory (this is usually not the case)

    rmdir -v ~/.local    

## 7 If no longer needed, remove python-scripts from $PATH

Manually remove these two lines:

    # Python scripts
    export PATH=$PATH":$HOME/.local/opt/python-scripts/"

Or use sed:
        
        sed -i '/# Python Scripts/{N;d;}' ~/.bashrc

# How to update?
    
## 1 Decrypt your files

    crycript -d file

## 3 Uninstall crycript (following the guide above) or remove old files

    rm -rv ~/.local/opt/crycript-main/*

## 4 Follow the installation guide
    
## 5 Encrypt your files with the new version

    crycript -e file
