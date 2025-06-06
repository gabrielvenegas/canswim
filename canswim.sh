#!/usr/bin/env bash
args=("$@")
#conda activate canswim
#pip install -e ./
python -m canswim "${args[@]}"

# run dashboard
# gradio src/canswim/dashboard.py
