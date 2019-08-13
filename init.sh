#!/bin/bash

apt update
apt -y full-upgrade

apt -y install vim net-tools git tree
apt-get -y install python-pip

echo -- PIP version: --
echo $(pip --version)


# -- Install sublime text editor --
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text
# -- add python autocompletion support
cd ~/.config/sublime-text-3/Packages/
git clone https://github.com/srusskih/SublimeJEDI.git "Jedi - Python autocompletion" 

# -- Install virtual environment -- 
echo "Installing virtualenv"
pip install virtualenv
virtualenv /venv
source /venv/bin/activate
pip install tensorflow tensorboard numpy dash dash-daq paramiko
deactivate

