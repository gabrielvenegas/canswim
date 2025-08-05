#!/bin/bash
set -e

echo -e "\033[32mStarting\033[0m"
echo -e "\033[32mInstalling python libs\033[0m"
pip install -e .
echo -e "\033[32mLibs installed, copying env into .env file\033[0m"
cp example.env .env
echo -e "\033[32m.env file created, installing vim\033[0m"
apt update
apt install -y vim
echo -e "\033[32mInstalling nano cause Gabriel is afraid of vim!!!!\033[0m"
apt install nano
echo -e "\033[32mNano installed, installing tmux\033[0m"
apt install -y tmux
echo -e "\033[32mTmux installed!\033[0m"
echo -e "\033[32mAdding my tmux config to the root\033[0m"
mv .tmux.conf ~/
echo -e "\033[32mTmux config added, ready to go\033[0m"
