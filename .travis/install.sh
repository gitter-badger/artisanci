#!/bin/bash

set -e
set -x

# Installing VirtualBox on sudo-enabled builds.
if [[ ! -z "$VIRTUALBOX" ]]; then
    sudo su -c "echo 'deb http://download.virtualbox.org/virtualbox/debian trusty contrib' >> /etc/apt/sources.list"
    wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
    wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install linux-headers-4.4.0-51-generic
    sudo apt-get install linux-headers-generic
    sudo apt-get install dkms
    sudo apt-get install virtualbox-5.1
    ls -Al /home/travis/virtualenv/python2.7.12/lib/python2.7/site-packages | grep v
    ls -Al /usr/lib/python2.7/site-packages
fi

# Installing Python on OSX.
if [[ "$(uname -s)" == 'Darwin' ]]; then
    # Install PyEnv
    git clone --depth 1 https://github.com/yyuu/pyenv.git ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    case "${TOXENV}" in
        py26)
            pyenv install 2.6.9
            pyenv global 2.6.9
            ;;
        py27)
            curl -O https://bootstrap.pypa.io/get-pip.py
            python get-pip.py --user
            ;;
        py33)
            pyenv install 3.3.6
            pyenv global 3.3.6
            ;;
        py34)
            pyenv install 3.4.5
            pyenv global 3.4.5
            ;;
        py35)
            pyenv install 3.5.2
            pyenv global 3.5.2
            ;;
        py36)
            pyenv install 3.6.0
            pyenv global 3.6.0
            ;;
    esac
    pyenv rehash
    pip install -U setuptools
    pip install --user virtualenv
else
    pip install virtualenv
fi

pip install tox
