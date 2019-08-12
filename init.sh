#!/bin/bash

apt update
apt -y full-upgrade

apt -y install vim net-tools git
apt-get -y install python-pip

echo -- PIP version: --
echo $(pip --version)

echo "Installing virtualenv"
pip install virtualenv
virtualenv /venv
source /venv/bin/activate
pip install tensorflow tensorboard numpy
deactivate
