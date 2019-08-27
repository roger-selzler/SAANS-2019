#!/bin/bash
set -e 

sudo apt update
sudo apt -y full-upgrade

sudo apt -y install vim net-tools git tree
sudo apt-get -y install python-pip

echo -- PIP version: --
echo $(pip --version)


# -- Install sublime text editor --
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text 

# -- Install virtual environment -- 
echo "Installing virtualenv"
pip install virtualenv
sudo virtualenv /venv
source /venv/bin/activate
pip install tensorflow tensorboard numpy dash dash-daq dash-bootstrap-components paramiko pandas jedi
# -- add python autocompletion support for Sublime
cd ~/.config/sublime-text-3/Packages/
[ -d "Jedi - Python auto completion" ] || git clone https://github.com/srusskih/SublimeJEDI.git "Jedi - Python auto completion"
# -- add autocompletion functionalities for vim
cd ~/ 
sudo apt-get install curl vim exuberant-ctags git ack-grep
sudo pip install pep8 flake8 pyflakes isort yapf 
[ -f ~/.vimrc ] && rm -rf ~/.vimrc && wget https://raw.github.com/fisadev/fisa-vim-config/master/.vimrc -O ~/.vimrc || wget https://raw.github.com/fisadev/      fisa-vim-config/master/.vimrc -O ~/.vimrc
vim -c :q! ~/.vimrc

# Create autocompletion for python on bash shell
[ -f ~/.pythonrc ] && rm -rf ~/.pythonrc && touch ~/.pythonrc && sudo echo "try:
    import readline
    import rlcompleter
    readline.parse_and_bind(\"tab: complete\")
except ImportError:
    print(\"Module readline not available.\")" > ~/.pythonrc

[ -f ~/.bashrc ] || touch ~/.bashrc 
grep -qxF 'export PYTHONSTARTUP=~/.pythonrc' ~/.bashrc && echo 'export PYTHONSTARTUP=~/.pythonrc already exists on ~/.bashrc' || echo 'export PYTHONSTARTUP=~/.pythonrc' >> ~/.bashrc

deactivate

