#!/bin/bash
set -e

echo "Starting"
echo "Installing python libs"
pip install -e .
echo "Libs installed, copying env into .env file"
cp example.env .env
echo ".env file created, installing vim"
apt update
apt install -y vim
echo "Installing nano for Gabriel cause he's afraid of Vim's superiority"
apt install nano
echo "Nano installed, installing tmux"
echo apt install tmux
echo "Tmux installed!"
