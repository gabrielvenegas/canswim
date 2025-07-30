#!/bin/bash

echo "Starting"
echo "Installing python libs"
pip install -e .
echo "Libs installed, copying env into .env file"
cp example.env .env
echo ".env file created, installing vim"
apt update
apt install vim
echo "Vim installed, installing tmux"
echo apt install tmux
