#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage: $0 <participant_id> <condition: touchpad|gesture>"
    exit 1
fi

pid=$1
cond=$2

python -m evaluation_study.app --pid "$pid" --condition "$cond" &

if [ "$cond" = "gesture" ]; then
    python -m main.app --silent &
fi

